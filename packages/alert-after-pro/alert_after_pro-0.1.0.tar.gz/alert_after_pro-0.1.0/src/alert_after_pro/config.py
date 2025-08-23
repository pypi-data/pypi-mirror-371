import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.aa'
        self.config_file = self.config_dir / 'config.yaml'
        self.config_data = {}
        self.load()
    
    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
                self.config_data = {}
    
    def save(self):
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any):
        self.config_data[key] = value
        self.save()
    
    def is_configured(self) -> bool:
        return bool(self.config_data.get('enabled_notifiers'))


def setup_wizard():
    print("\n🚀 Alert After Pro Setup Wizard\n")
    print("This wizard will help you configure your notification channels.")
    print("You can always run 'aa --setup' again to reconfigure.\n")
    
    config = Config()
    enabled_notifiers = []
    
    print("Available notification channels:")
    print("1. Telegram")
    print("2. Ntfy (self-hosted or ntfy.sh)")
    print("3. DingDing (钉钉)")
    print("4. SMS (Twilio)")
    print("5. Pushover")
    
    channels = input("\nWhich channels would you like to configure? (comma-separated numbers): ")
    
    if not channels.strip():
        print("No channels selected. Setup cancelled.")
        return
    
    selected = [int(x.strip()) for x in channels.split(',') if x.strip().isdigit()]
    
    if 1 in selected:
        print("\n📱 Configuring Telegram:")
        print("1. Create a bot using @BotFather on Telegram")
        print("2. Get your bot token")
        print("3. Send a message to your bot")
        print("4. Get your chat ID from: https://api.telegram.org/bot<TOKEN>/getUpdates")
        
        token = input("Bot Token: ").strip()
        chat_id = input("Chat ID: ").strip()
        
        if token and chat_id:
            config.set('telegram', {
                'bot_token': token,
                'chat_id': chat_id
            })
            enabled_notifiers.append('telegram')
            print("✓ Telegram configured")
    
    if 2 in selected:
        print("\n🔔 Configuring Ntfy:")
        server = input("Ntfy server (default: https://ntfy.sh): ").strip()
        if not server:
            server = "https://ntfy.sh"
        
        topic = input("Topic name: ").strip()
        auth_required = input("Authentication required? (y/n): ").lower() == 'y'
        
        ntfy_config = {
            'server': server,
            'topic': topic
        }
        
        if auth_required:
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            ntfy_config['username'] = username
            ntfy_config['password'] = password
        
        config.set('ntfy', ntfy_config)
        enabled_notifiers.append('ntfy')
        print("✓ Ntfy configured")
    
    if 3 in selected:
        print("\n💬 Configuring DingDing:")
        print("1. Create a robot in your DingDing group")
        print("2. Get the webhook URL")
        
        webhook = input("Webhook URL: ").strip()
        secret = input("Secret (optional, for signature): ").strip()
        
        dingding_config = {'webhook': webhook}
        if secret:
            dingding_config['secret'] = secret
        
        config.set('dingding', dingding_config)
        enabled_notifiers.append('dingding')
        print("✓ DingDing configured")
    
    if 4 in selected:
        print("\n📲 Configuring SMS (Twilio):")
        print("Get your credentials from https://console.twilio.com")
        
        account_sid = input("Account SID: ").strip()
        auth_token = input("Auth Token: ").strip()
        from_number = input("From Number (with country code): ").strip()
        to_number = input("To Number (with country code): ").strip()
        
        config.set('sms', {
            'provider': 'twilio',
            'account_sid': account_sid,
            'auth_token': auth_token,
            'from_number': from_number,
            'to_number': to_number
        })
        enabled_notifiers.append('sms')
        print("✓ SMS configured")
    
    if 5 in selected:
        print("\n📣 Configuring Pushover:")
        print("Get your tokens from https://pushover.net")
        
        app_token = input("Application Token: ").strip()
        user_key = input("User Key: ").strip()
        
        config.set('pushover', {
            'app_token': app_token,
            'user_key': user_key
        })
        enabled_notifiers.append('pushover')
        print("✓ Pushover configured")
    
    config.set('enabled_notifiers', enabled_notifiers)
    
    capture = input("\nCapture command output in notifications? (y/n): ").lower() == 'y'
    config.set('capture_output', capture)
    
    print(f"\n✨ Setup complete! Configured {len(enabled_notifiers)} notification channel(s).")
    print("Test your configuration with: aa --test")
    print("Start using: aa <your-command>")