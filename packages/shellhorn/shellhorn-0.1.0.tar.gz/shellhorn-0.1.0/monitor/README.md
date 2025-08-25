# Conch Monitor 🐚👁️

A lightweight Docker service that monitors MQTT for orphaned conch commands and sends alerts when commands die unexpectedly.

## What It Does

Conch Monitor solves the "when it dies unexpectedly" problem by:
1. **Tracking active commands** - Listens for `conch/start` messages
2. **Detecting orphans** - Commands that started but never reported completion
3. **Sending alerts** - Pushover notifications when orphaned commands are detected

## Quick Start

### 1. Setup Configuration

```bash
# Copy example files
cp config/config.json.example config/config.json
cp config/secrets.json.example config/secrets.json
cp .env.example .env

# Edit secrets (RECOMMENDED approach)
nano config/secrets.json
```

**config/secrets.json:**
```json
{
  "mqtt_username": "your_mqtt_user",
  "mqtt_password": "your_mqtt_pass", 
  "pushover_token": "your_app_token",
  "pushover_user": "your_user_key"
}
```

### 2. Run with Docker Compose

```bash
# Edit environment variables
nano .env

# Start the monitor
docker-compose up -d

# Check logs
docker-compose logs -f conch-monitor
```

### 3. Test It

```bash
# Start a command that will be "orphaned" (kill the process manually)
conch sleep 300 &

# Kill the process (simulate crash)
kill %1

# Monitor will detect it as orphaned after timeout (default 30 minutes)
```

## Configuration Options

### Timeouts
- `CONCH_TIMEOUT_MINUTES=30` - How long before a command is considered orphaned
- `CONCH_CHECK_INTERVAL=60` - How often to check for orphans (seconds)
- `CONCH_STATUS_INTERVAL=300` - How often to log status (seconds)

### MQTT Settings
- `MQTT_BROKER=localhost` - MQTT broker hostname
- `MQTT_PORT=1883` - MQTT broker port
- `MQTT_TOPIC_PREFIX=conch` - Topic prefix to monitor

## Security Best Practices

### ✅ Recommended: Secrets File
```bash
# Store secrets in mounted file (read-only)
echo '{"pushover_token":"abc123"}' > config/secrets.json
chmod 600 config/secrets.json
```

### ⚠️ Alternative: Environment Variables
```bash
# Less secure, but works
export PUSHOVER_TOKEN=abc123
export PUSHOVER_USER=xyz789
```

### Docker Security Features
- **Non-root user** (UID 1001)
- **Read-only filesystem**
- **Resource limits** (64MB RAM, 0.1 CPU)
- **Minimal privileges**
- **Health checks**

## Monitoring Scenarios

### Home Lab Setup
```yaml
# docker-compose.yml
services:
  conch-monitor:
    environment:
      - MQTT_BROKER=mqtt.homelab.local
      - CONCH_TIMEOUT_MINUTES=15  # Shorter timeout
```

### Production Setup
```yaml
services:
  conch-monitor:
    environment:
      - MQTT_BROKER=mqtt.prod.company.com
      - CONCH_TIMEOUT_MINUTES=60  # Longer timeout
      - CONCH_CHECK_INTERVAL=30   # Check more frequently
```

### Multiple Environments
```bash
# Different configs for different environments
docker run -d --name conch-monitor-dev \
  -v ./config-dev:/etc/conch-monitor:ro \
  -e MQTT_BROKER=mqtt-dev.local \
  conch-monitor

docker run -d --name conch-monitor-prod \
  -v ./config-prod:/etc/conch-monitor:ro \
  -e MQTT_BROKER=mqtt-prod.local \
  conch-monitor
```

## MQTT Topics Monitored

- `conch/start` - Command started (begins tracking)
- `conch/complete` - Command finished successfully (stops tracking)
- `conch/error` - Command had an error (stops tracking)  
- `conch/interrupt` - Command was interrupted (stops tracking)

## Alert Message Format

When an orphaned command is detected:

```
🚨 Orphaned Command Detected

Command: python3 train_model.py --epochs 100
Client: laptop-123
Started: 2024-08-24 14:30:15
Age: 45.2 minutes
PID: 12345

This command started but never reported completion.
The process may have crashed or the machine may be unreachable.
```

## Troubleshooting

### Check MQTT Connection
```bash
# Test MQTT connectivity from container
docker exec conch-monitor python -c "
import socket
s = socket.socket()
s.settimeout(5)
result = s.connect_ex(('mqtt-broker', 1883))
print('MQTT OK' if result == 0 else 'MQTT FAILED')
"
```

### Debug Logging
```bash
# Enable debug logging
docker-compose exec conch-monitor python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
"
```

### Manual Testing
```bash
# Send test MQTT message
mosquitto_pub -h localhost -t conch/start -m '{
  "command": "test-command", 
  "client_id": "test-client",
  "timestamp": "2024-08-24T14:30:00",
  "pid": 12345
}'
```

## Resource Usage

- **Memory**: ~16MB typical, 64MB limit
- **CPU**: ~0.05% typical, 0.1% limit  
- **Network**: Minimal (MQTT messages only)
- **Storage**: Stateless (no persistence needed)

Perfect for running alongside other services in resource-constrained environments like Raspberry Pi or small VPS instances.