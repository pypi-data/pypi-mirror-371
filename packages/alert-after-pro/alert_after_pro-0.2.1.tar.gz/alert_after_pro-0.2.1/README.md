# Alert After Pro 🚀

*Read this in other languages: [English](README.md), [中文](README_zh.md)*

Get notified when your commands complete! Simply prefix any command with `aa` and receive notifications via Telegram, SMS, DingDing (钉钉), Ntfy, or Pushover.

Perfect for long-running builds, tests, deployments, or any command you want to monitor remotely.

## ✨ Features

- **Super Simple**: Just prefix your command with `aa`
- **Multiple Channels**: Telegram, SMS (Twilio), DingDing, Ntfy, Pushover
- **Rich Notifications**: Command status, duration, exit code, hostname
- **Cross-platform**: Works on Linux, macOS, and Windows
- **Zero Dependencies**: Minimal core dependencies
- **Configurable**: Optional command output capture, multiple simultaneous channels

## 🚀 Quick Start

### Installation

```bash
pip install alert-after-pro
```

That's it! One line installation.

### Setup

Run the configuration wizard:

```bash
aa --setup
```

Choose your notification channels and provide the necessary credentials.

### Usage

Simply prefix any command with `aa`:

```bash
# Examples
aa make build
aa pytest tests/
aa docker-compose up
aa "sleep 10 && echo done"
aa npm install && npm run build
```

## 📱 Supported Notification Channels

### Telegram
1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Send a message to your bot
4. Get your chat ID from: `https://api.telegram.org/bot<TOKEN>/getUpdates`

### Ntfy (ntfy.sh or self-hosted)
- **Server**: Use `https://ntfy.sh` or your own server
- **Topic**: Any topic name (e.g., "my-alerts")
- **Auth**: Optional username/password for private servers

### DingDing (钉钉)
1. Create a robot in your DingDing group
2. Get the webhook URL
3. Optional: Enable signature verification with secret

### SMS (via Twilio)
1. Sign up at [Twilio](https://www.twilio.com)
2. Get your Account SID and Auth Token
3. Get a phone number

### Pushover
1. Sign up at [Pushover](https://pushover.net)
2. Create an application
3. Get your app token and user key

## 🔧 Command Options

```bash
aa --help                # Show help
aa --setup               # Run configuration wizard
aa --test                # Send test notification
aa --silent <command>    # Run command without notifications
```

## 📁 Configuration

Configuration is stored in `~/.aa/config.yaml`:

```yaml
enabled_notifiers:
  - telegram
  - ntfy

capture_output: false

telegram:
  bot_token: "your_bot_token"
  chat_id: "your_chat_id"

ntfy:
  server: "https://ntfy.sh"
  topic: "my-alerts"
  username: "optional"
  password: "optional"

dingding:
  webhook: "https://oapi.dingtalk.com/robot/send?access_token=..."
  secret: "optional_secret"

sms:
  provider: "twilio"
  account_sid: "your_account_sid"
  auth_token: "your_auth_token"
  from_number: "+1234567890"
  to_number: "+0987654321"

pushover:
  app_token: "your_app_token"
  user_key: "your_user_key"
```

## 📋 What You'll Get

Rich notifications include:
- ✅/❌ Command status (success/failure)
- 🖥️ Hostname
- 💻 Full command
- ⏱️ Execution duration
- 📊 Exit code
- 🕐 Start and end times
- 📋 Command output (optional)
- ❌ Error messages (on failure)

## 🛠️ Development

### Local Development

```bash
git clone https://github.com/alert-after-pro/alert-after-pro
cd alert-after-pro
pip install -e .
```

### Testing

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Test specific notifier
aa --test
```

### Project Structure

```
alert-after-pro/
├── src/alert_after_pro/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration management
│   └── notifiers/           # Notification implementations
│       ├── base.py          # Abstract base class
│       ├── telegram.py
│       ├── ntfy.py
│       ├── dingding.py
│       ├── sms.py
│       └── pushover.py
├── setup.py
└── requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas for contribution:

- New notification channels
- Improved error handling
- Better message formatting
- Documentation improvements
- Testing

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by [alert-after](https://github.com/frewsxcv/alert-after). Built for developers who want to be notified when their long-running commands complete.

---

**Happy coding! 🎉**

Made with ❤️ for developers who like to step away from their terminals.