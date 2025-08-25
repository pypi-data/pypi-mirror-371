#!/usr/bin/env python3
"""
Integration tests for Conch Monitor using embedded MQTT broker.
"""

import json
import time
import threading
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import tempfile
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'monitor'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'conch'))

import paho.mqtt.client as mqtt
from paho.mqtt import subscribe

from conch_monitor import ConchMonitor, ActiveCommand


class EmbeddedMQTTBroker:
    """Lightweight MQTT broker for testing."""
    
    def __init__(self, port=1883):
        self.port = port
        self.clients = {}
        self.subscriptions = {}
        self.messages = []
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the embedded broker."""
        # For testing, we'll use a simple message relay approach
        self.running = True
        return True
    
    def stop(self):
        """Stop the embedded broker."""
        self.running = False
    
    def publish_message(self, topic, payload):
        """Simulate publishing a message."""
        message = {
            'topic': topic,
            'payload': payload,
            'timestamp': datetime.now()
        }
        self.messages.append(message)
        
        # Notify subscribers
        for client_id, client_subs in self.subscriptions.items():
            if any(self._topic_matches(topic, sub) for sub in client_subs):
                if client_id in self.clients:
                    # Simulate message delivery
                    self.clients[client_id]['callback'](topic, payload)
    
    def _topic_matches(self, topic, subscription):
        """Check if topic matches subscription pattern."""
        # Simple wildcard matching
        if subscription.endswith('#'):
            return topic.startswith(subscription[:-1])
        if subscription.endswith('+'):
            # More complex matching would be needed for full + support
            return topic.startswith(subscription[:-1])
        return topic == subscription
    
    def register_client(self, client_id, callback):
        """Register a client with callback."""
        self.clients[client_id] = {'callback': callback}
    
    def subscribe(self, client_id, topics):
        """Subscribe client to topics."""
        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = []
        self.subscriptions[client_id].extend(topics)


class MockMQTTClient:
    """Mock MQTT client for testing."""
    
    def __init__(self, broker, client_id):
        self.broker = broker
        self.client_id = client_id
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None
        self.connected = False
        
    def username_pw_set(self, username, password):
        """Mock username/password setting."""
        pass
    
    def connect(self, host, port, keepalive):
        """Mock connection."""
        self.connected = True
        self.broker.register_client(self.client_id, self._handle_message)
        if self.on_connect:
            self.on_connect(self, None, None, 0)
    
    def disconnect(self):
        """Mock disconnection."""
        self.connected = False
        if self.on_disconnect:
            self.on_disconnect(self, None, 0)
    
    def subscribe(self, topic, qos=0):
        """Mock subscription."""
        self.broker.subscribe(self.client_id, [topic])
    
    def loop_start(self):
        """Mock loop start."""
        pass
    
    def loop_stop(self):
        """Mock loop stop."""
        pass
    
    def _handle_message(self, topic, payload):
        """Handle incoming message."""
        if self.on_message:
            # Create a mock message object
            msg = MagicMock()
            msg.topic = topic
            msg.payload = payload.encode() if isinstance(payload, str) else payload
            self.on_message(self, None, msg)


class TestConchMonitorIntegration(unittest.TestCase):
    """Integration tests for Conch Monitor."""
    
    def setUp(self):
        """Set up test environment."""
        self.broker = EmbeddedMQTTBroker()
        self.broker.start()
        
        # Create temporary config
        self.config = {
            'mqtt': {
                'broker_host': 'localhost',
                'broker_port': 1883,
                'topic_prefix': 'test_conch'
            },
            'monitoring': {
                'timeout_minutes': 1,  # Short timeout for testing
                'check_interval_seconds': 1,
                'status_interval_seconds': 10
            },
            'client_id': 'test-monitor',
            'secrets_file': '/dev/null'  # No secrets for testing
        }
        
        # Mock MQTT client creation
        self.original_mqtt_client = mqtt.Client
        mqtt.Client = lambda client_id: MockMQTTClient(self.broker, client_id)
        
        self.monitor = ConchMonitor(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.monitor.running = False
        self.broker.stop()
        # Restore original MQTT client
        mqtt.Client = self.original_mqtt_client
    
    @patch('conch_monitor.ConchMonitor.send_pushover_alert')
    def test_orphan_detection(self, mock_pushover):
        """Test detection of orphaned commands."""
        # Setup monitor
        self.monitor.setup_mqtt()
        
        # Simulate command start
        start_message = {
            'command': 'python3 test_script.py',
            'client_id': 'test-client',
            'timestamp': (datetime.now() - timedelta(minutes=2)).isoformat(),
            'pid': 12345
        }
        
        self.broker.publish_message(
            'test_conch/start',
            json.dumps(start_message)
        )
        
        # Wait a moment for message processing
        time.sleep(0.1)
        
        # Check that command is being tracked
        self.assertEqual(len(self.monitor.active_commands), 1)
        
        # Run orphan check (command should be detected as orphaned)
        self.monitor.check_orphaned_commands()
        
        # Verify orphan was detected and alert was sent
        mock_pushover.assert_called_once()
        
        # Verify command was removed from tracking
        self.assertEqual(len(self.monitor.active_commands), 0)
    
    def test_normal_command_lifecycle(self):
        """Test normal command start and completion."""
        # Setup monitor
        self.monitor.setup_mqtt()
        
        # Simulate command start
        start_message = {
            'command': 'echo hello',
            'client_id': 'test-client',
            'timestamp': datetime.now().isoformat(),
            'pid': 12345
        }
        
        self.broker.publish_message(
            'test_conch/start',
            json.dumps(start_message)
        )
        
        time.sleep(0.1)
        
        # Check that command is being tracked
        self.assertEqual(len(self.monitor.active_commands), 1)
        
        # Simulate command completion
        complete_message = {
            'command': 'echo hello',
            'client_id': 'test-client',
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'duration': 0.5
        }
        
        self.broker.publish_message(
            'test_conch/complete',
            json.dumps(complete_message)
        )
        
        time.sleep(0.1)
        
        # Verify command was removed from tracking
        self.assertEqual(len(self.monitor.active_commands), 0)
    
    def test_command_failure_handling(self):
        """Test handling of command failures."""
        # Setup monitor
        self.monitor.setup_mqtt()
        
        # Simulate command start
        start_message = {
            'command': 'false',  # Command that fails
            'client_id': 'test-client',
            'timestamp': datetime.now().isoformat(),
            'pid': 12345
        }
        
        self.broker.publish_message(
            'test_conch/start',
            json.dumps(start_message)
        )
        
        time.sleep(0.1)
        self.assertEqual(len(self.monitor.active_commands), 1)
        
        # Simulate command error
        error_message = {
            'command': 'false',
            'client_id': 'test-client',
            'timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'return_code': 1
        }
        
        self.broker.publish_message(
            'test_conch/error',
            json.dumps(error_message)
        )
        
        time.sleep(0.1)
        
        # Verify command was removed from tracking (not orphaned)
        self.assertEqual(len(self.monitor.active_commands), 0)
    
    def test_interrupt_handling(self):
        """Test handling of interrupted commands."""
        # Setup monitor
        self.monitor.setup_mqtt()
        
        # Simulate command start
        start_message = {
            'command': 'sleep 100',
            'client_id': 'test-client',
            'timestamp': datetime.now().isoformat(),
            'pid': 12345
        }
        
        self.broker.publish_message(
            'test_conch/start',
            json.dumps(start_message)
        )
        
        time.sleep(0.1)
        self.assertEqual(len(self.monitor.active_commands), 1)
        
        # Simulate command interruption
        interrupt_message = {
            'command': 'sleep 100',
            'client_id': 'test-client',
            'timestamp': datetime.now().isoformat(),
            'status': 'interrupted',
            'duration': 5.0
        }
        
        self.broker.publish_message(
            'test_conch/interrupt',
            json.dumps(interrupt_message)
        )
        
        time.sleep(0.1)
        
        # Verify command was removed from tracking
        self.assertEqual(len(self.monitor.active_commands), 0)
    
    def test_multiple_clients(self):
        """Test monitoring commands from multiple clients."""
        # Setup monitor
        self.monitor.setup_mqtt()
        
        # Start commands from different clients
        for i in range(3):
            start_message = {
                'command': f'task_{i}',
                'client_id': f'client-{i}',
                'timestamp': datetime.now().isoformat(),
                'pid': 12345 + i
            }
            
            self.broker.publish_message(
                'test_conch/start',
                json.dumps(start_message)
            )
        
        time.sleep(0.1)
        
        # All commands should be tracked
        self.assertEqual(len(self.monitor.active_commands), 3)
        
        # Complete one command
        complete_message = {
            'command': 'task_1',
            'client_id': 'client-1',
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        self.broker.publish_message(
            'test_conch/complete',
            json.dumps(complete_message)
        )
        
        time.sleep(0.1)
        
        # Two commands should remain
        self.assertEqual(len(self.monitor.active_commands), 2)
    
    def test_config_loading(self):
        """Test configuration loading from various sources."""
        # Test with temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_config = {
                'mqtt': {
                    'broker_host': 'test-broker',
                    'broker_port': 1234
                },
                'monitoring': {
                    'timeout_minutes': 45
                }
            }
            json.dump(test_config, f)
            config_file = f.name
        
        try:
            # Mock environment to point to our test config
            with patch.dict('os.environ', {'CONCH_MONITOR_CONFIG': config_file}):
                from conch_monitor import load_config
                loaded_config = load_config()
                
                self.assertEqual(loaded_config['mqtt']['broker_host'], 'test-broker')
                self.assertEqual(loaded_config['mqtt']['broker_port'], 1234)
                self.assertEqual(loaded_config['monitoring']['timeout_minutes'], 45)
        finally:
            os.unlink(config_file)


class TestConchIntegration(unittest.TestCase):
    """Integration tests for the main conch command with MQTT."""
    
    def setUp(self):
        """Set up test environment."""
        self.broker = EmbeddedMQTTBroker()
        self.broker.start()
        
        # Mock MQTT client
        self.original_mqtt_client = mqtt.Client
        mqtt.Client = lambda client_id: MockMQTTClient(self.broker, client_id)
    
    def tearDown(self):
        """Clean up test environment."""
        self.broker.stop()
        mqtt.Client = self.original_mqtt_client
    
    @patch('conch.notifiers.MQTTNotifier._publish')
    def test_conch_mqtt_integration(self, mock_publish):
        """Test that conch properly publishes to MQTT."""
        from conch.notifiers import MQTTNotifier
        
        # Create MQTT notifier
        notifier = MQTTNotifier(
            broker_host='localhost',
            broker_port=1883,
            topic_prefix='test_conch'
        )
        
        # Test start notification
        notifier.notify_start('echo test', 12345)
        mock_publish.assert_called_with('start', {
            'command': 'echo test',
            'pid': 12345,
            'status': 'started'
        })
        
        # Test success notification  
        notifier.notify_success('echo test', 0.5, 0)
        mock_publish.assert_called_with('complete', {
            'command': 'echo test',
            'duration': 0.5,
            'return_code': 0,
            'status': 'success'
        })


if __name__ == '__main__':
    # Set up test environment
    print("Running Conch Monitor Integration Tests")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)