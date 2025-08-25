#!/usr/bin/env python3
"""
Conch Monitor - Watches for orphaned commands via MQTT.

Tracks commands that start but never finish (due to crashes, network issues, etc.)
and sends alerts when commands are detected as orphaned.
"""

import json
import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

import paho.mqtt.client as mqtt
import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('conch-monitor')


@dataclass
class ActiveCommand:
    """Represents an active command being monitored."""
    command: str
    client_id: str
    start_time: datetime
    pid: Optional[int] = None
    last_seen: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.last_seen:
            data['last_seen'] = self.last_seen.isoformat()
        return data

    @property
    def age_seconds(self) -> float:
        """Get age of command in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def is_orphaned(self, timeout_minutes: int) -> bool:
        """Check if command is considered orphaned."""
        return self.age_seconds > (timeout_minutes * 60)


class ConchMonitor:
    """Monitors MQTT for conch command lifecycle and detects orphans."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_commands: Dict[str, ActiveCommand] = {}
        self.mqtt_client = None
        self.running = False
        self.lock = threading.Lock()

    def load_secrets(self) -> Dict[str, Any]:
        """Load secrets from file or environment variables."""
        secrets = {}
        
        # Try to load from secrets file first (recommended)
        secrets_file = self.config.get('secrets_file', '/etc/conch-monitor/secrets.json')
        if os.path.exists(secrets_file):
            logger.info(f"Loading secrets from {secrets_file}")
            try:
                with open(secrets_file, 'r') as f:
                    secrets = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load secrets file: {e}")
        
        # Environment variables override file secrets
        env_secrets = {
            'mqtt_username': os.getenv('MQTT_USERNAME'),
            'mqtt_password': os.getenv('MQTT_PASSWORD'),
            'pushover_token': os.getenv('PUSHOVER_TOKEN'),
            'pushover_user': os.getenv('PUSHOVER_USER'),
            'pushover_device': os.getenv('PUSHOVER_DEVICE'),
        }
        
        # Merge, preferring env vars over file
        for key, value in env_secrets.items():
            if value is not None:
                secrets[key] = value
        
        return secrets

    def setup_mqtt(self):
        """Setup MQTT client connection."""
        secrets = self.load_secrets()
        
        client_id = self.config.get('client_id', f"conch-monitor-{int(time.time())}")
        self.mqtt_client = mqtt.Client(client_id=client_id)
        
        # Authentication
        username = secrets.get('mqtt_username')
        password = secrets.get('mqtt_password')
        if username and password:
            self.mqtt_client.username_pw_set(username, password)
            logger.info(f"MQTT authentication configured for user: {username}")
        
        # Callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message
        
        # Connect
        broker_host = self.config['mqtt']['broker_host']
        broker_port = self.config['mqtt']['broker_port']
        
        logger.info(f"Connecting to MQTT broker: {broker_host}:{broker_port}")
        self.mqtt_client.connect(broker_host, broker_port, 60)

    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            topic_prefix = self.config['mqtt']['topic_prefix']
            topics = [
                f"{topic_prefix}/start",
                f"{topic_prefix}/complete", 
                f"{topic_prefix}/error",
                f"{topic_prefix}/interrupt"
            ]
            for topic in topics:
                client.subscribe(topic, qos=1)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        if rc != 0:
            logger.warning("Unexpected MQTT disconnection")
        else:
            logger.info("MQTT disconnected")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            topic_parts = msg.topic.split('/')
            event_type = topic_parts[-1]  # start, complete, error, interrupt
            
            payload = json.loads(msg.payload.decode())
            command_key = f"{payload['client_id']}:{payload['command']}"
            
            with self.lock:
                if event_type == "start":
                    self.handle_command_start(command_key, payload)
                elif event_type in ["complete", "error", "interrupt"]:
                    self.handle_command_end(command_key, payload, event_type)
            
        except Exception as e:
            logger.error(f"Error processing message from {msg.topic}: {e}")

    def handle_command_start(self, command_key: str, payload: Dict[str, Any]):
        """Handle command start event."""
        command = ActiveCommand(
            command=payload['command'],
            client_id=payload['client_id'],
            start_time=datetime.fromisoformat(payload['timestamp']),
            pid=payload.get('pid'),
            last_seen=datetime.now()
        )
        
        self.active_commands[command_key] = command
        logger.info(f"Tracking new command: {command.command} (client: {command.client_id})")

    def handle_command_end(self, command_key: str, payload: Dict[str, Any], event_type: str):
        """Handle command end event (complete/error/interrupt)."""
        if command_key in self.active_commands:
            command = self.active_commands.pop(command_key)
            duration = command.age_seconds
            logger.info(f"Command finished ({event_type}): {command.command} after {duration:.2f}s")
        else:
            logger.warning(f"Received {event_type} for unknown command: {payload.get('command')}")

    def check_orphaned_commands(self):
        """Check for orphaned commands and send alerts."""
        timeout_minutes = self.config['monitoring']['timeout_minutes']
        
        with self.lock:
            orphaned = []
            for key, command in list(self.active_commands.items()):
                if command.is_orphaned(timeout_minutes):
                    orphaned.append(command)
                    # Remove from active tracking after alerting
                    del self.active_commands[key]
        
        for command in orphaned:
            logger.warning(f"Orphaned command detected: {command.command} (age: {command.age_seconds/60:.1f} minutes)")
            self.send_orphan_alert(command)

    def send_orphan_alert(self, command: ActiveCommand):
        """Send alert for orphaned command."""
        secrets = self.load_secrets()
        
        # Prepare alert message
        age_minutes = command.age_seconds / 60
        message = (
            f"🚨 Orphaned Command Detected\n\n"
            f"Command: {command.command}\n"
            f"Client: {command.client_id}\n"
            f"Started: {command.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Age: {age_minutes:.1f} minutes\n"
            f"PID: {command.pid or 'Unknown'}\n\n"
            f"This command started but never reported completion. "
            f"The process may have crashed or the machine may be unreachable."
        )
        
        # Send Pushover notification
        pushover_token = secrets.get('pushover_token')
        pushover_user = secrets.get('pushover_user')
        
        if pushover_token and pushover_user:
            try:
                self.send_pushover_alert(pushover_token, pushover_user, 
                                       secrets.get('pushover_device'), message)
                logger.info(f"Pushover alert sent for orphaned command: {command.command}")
            except Exception as e:
                logger.error(f"Failed to send Pushover alert: {e}")
        else:
            logger.warning("Pushover credentials not configured, skipping notification")

    def send_pushover_alert(self, token: str, user: str, device: Optional[str], message: str):
        """Send Pushover notification."""
        data = {
            'token': token,
            'user': user,
            'message': message,
            'title': '🐚 Conch Monitor Alert',
            'priority': 1,  # High priority
        }
        
        if device:
            data['device'] = device
        
        response = requests.post('https://api.pushover.net/1/messages.json', 
                               data=data, timeout=10)
        response.raise_for_status()

    def status_report(self):
        """Generate status report."""
        with self.lock:
            active_count = len(self.active_commands)
            if active_count > 0:
                logger.info(f"Currently monitoring {active_count} active command(s):")
                for key, command in self.active_commands.items():
                    logger.info(f"  - {command.command} (age: {command.age_seconds/60:.1f}m)")
            else:
                logger.info("No active commands being monitored")

    def run(self):
        """Main monitoring loop."""
        logger.info("Starting Conch Monitor")
        
        # Setup MQTT
        self.setup_mqtt()
        
        # Start MQTT client
        self.mqtt_client.loop_start()
        self.running = True
        
        check_interval = self.config['monitoring']['check_interval_seconds']
        status_interval = self.config['monitoring']['status_interval_seconds']
        
        last_status_report = time.time()
        
        try:
            while self.running:
                time.sleep(check_interval)
                
                # Check for orphaned commands
                self.check_orphaned_commands()
                
                # Periodic status report
                if time.time() - last_status_report > status_interval:
                    self.status_report()
                    last_status_report = time.time()
                    
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        finally:
            self.running = False
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("Conch Monitor stopped")


def load_config() -> Dict[str, Any]:
    """Load configuration from file or use defaults."""
    config_file = os.getenv('CONCH_MONITOR_CONFIG', '/etc/conch-monitor/config.json')
    
    default_config = {
        'mqtt': {
            'broker_host': os.getenv('MQTT_BROKER', 'localhost'),
            'broker_port': int(os.getenv('MQTT_PORT', '1883')),
            'topic_prefix': os.getenv('MQTT_TOPIC_PREFIX', 'conch')
        },
        'monitoring': {
            'timeout_minutes': int(os.getenv('CONCH_TIMEOUT_MINUTES', '30')),
            'check_interval_seconds': int(os.getenv('CONCH_CHECK_INTERVAL', '60')),
            'status_interval_seconds': int(os.getenv('CONCH_STATUS_INTERVAL', '300'))
        },
        'client_id': os.getenv('CONCH_CLIENT_ID'),
        'secrets_file': os.getenv('CONCH_SECRETS_FILE', '/etc/conch-monitor/secrets.json')
    }
    
    if os.path.exists(config_file):
        logger.info(f"Loading configuration from {config_file}")
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                # Merge file config with defaults
                for section in default_config:
                    if section in file_config:
                        if isinstance(default_config[section], dict):
                            default_config[section].update(file_config[section])
                        else:
                            default_config[section] = file_config[section]
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            logger.info("Using default configuration")
    else:
        logger.info(f"No config file found at {config_file}, using defaults")
    
    return default_config


def main():
    """Main entry point."""
    config = load_config()
    monitor = ConchMonitor(config)
    monitor.run()


if __name__ == '__main__':
    main()