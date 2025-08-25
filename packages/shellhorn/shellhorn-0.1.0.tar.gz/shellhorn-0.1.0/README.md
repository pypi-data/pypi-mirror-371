# Conch 🐚

A lightweight command wrapper with notification and monitoring capabilities. Perfect for long-running commands that you want to be notified about when they complete.

## Features

- **Command Wrapping**: Prepend any command with `conch` to monitor it
- **Pushover Notifications**: Get notified on your phone when commands complete
- **MQTT Monitoring**: Centralized monitoring via MQTT for lightweight distributed setups
- **Failure Detection**: Automatic notification when commands fail unexpectedly
- **Simple Configuration**: Easy setup via config file or environment variables

## Installation

```bash
cd conch
pip install -e .
```

## Quick Start

### Basic Usage
```bash
# Wrap any command
conch python3 my-long-training-script.py
conch make build
conch npm test
```

### With Pushover Notifications
```bash
# Set up Pushover (one time)
conch config set pushover.app_token YOUR_APP_TOKEN
conch config set pushover.user_key YOUR_USER_KEY  
conch config set pushover.enabled true

# Now all commands will send notifications
conch python3 training.py
```

### With MQTT Monitoring
```bash
# Set up MQTT (one time)
conch config set mqtt.broker_host mqtt.example.com
conch config set mqtt.enabled true

# Commands will publish status to MQTT
conch ./long-running-process.sh
```

## Configuration

### Config File
Configuration is stored in `~/.config/conch/config.json`:

```json
{
  "notifications": {
    "pushover": {
      "enabled": true,
      "app_token": "your_app_token",
      "user_key": "your_user_key",
      "device": null
    },
    "mqtt": {
      "enabled": true,
      "broker_host": "localhost",
      "broker_port": 1883,
      "topic_prefix": "conch",
      "username": null,
      "password": null
    },
    "console": {
      "enabled": false
    }
  }
}
```

### Environment Variables
You can also configure via environment variables:

```bash
export CONCH_PUSHOVER_TOKEN=your_app_token
export CONCH_PUSHOVER_USER=your_user_key
export CONCH_MQTT_BROKER=mqtt.example.com
export CONCH_CONSOLE_NOTIFICATIONS=true

conch python3 script.py
```

### CLI Options
Override config on-the-fly:

```bash
conch --pushover-token=xxx --pushover-user=yyy python3 script.py
conch --mqtt-broker=localhost --console-notifications python3 script.py
```

## Commands

### Configuration Management
```bash
# Show current config
conch config show

# Set configuration values
conch config set pushover.app_token abc123
conch config set mqtt.broker_host localhost
conch config set pushover.enabled true

# Test notifications
conch config test
```

### Version
```bash
conch version
```

## MQTT Topics

When MQTT monitoring is enabled, conch publishes to these topics:

- `conch/start` - Command started
- `conch/complete` - Command completed (success or failure)
- `conch/error` - Unexpected errors
- `conch/interrupt` - Command interrupted (Ctrl+C)

Message format:
```json
{
  "command": "python3 script.py",
  "status": "success",
  "duration": 123.45,
  "timestamp": "2024-01-01T12:00:00",
  "client_id": "conch_123456789"
}
```

## Examples

### Machine Learning Training
```bash
# Get notified when training completes
conch python3 train_model.py --epochs 100
```

### Build Systems
```bash
# Monitor CI/CD pipeline steps
conch make clean
conch make build
conch make test
conch make deploy
```

### Data Processing
```bash
# Long-running data pipeline
conch python3 process_large_dataset.py
```

## Why "Conch"?

- **Shell** reference (command wrapper)
- **Echo** functionality (notifications)  
- **Listen** for completion (monitoring)

Plus, conch shells are beautiful and make sounds when you listen to them! 🐚