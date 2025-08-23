import requests
from typing import Dict, Any
from .base import BaseNotifier


class TelegramNotifier(BaseNotifier):
    def send(self, data: Dict[str, Any]) -> bool:
        telegram_config = self.config.get('telegram', {})
        bot_token = telegram_config.get('bot_token')
        chat_id = telegram_config.get('chat_id')
        
        if not bot_token or not chat_id:
            raise ValueError("Telegram bot_token and chat_id are required")
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        message = self.format_telegram_message(data)
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            raise Exception(f"Failed to send Telegram notification: {e}")
    
    def format_telegram_message(self, data: Dict[str, Any]) -> str:
        status_emoji = "✅" if data.get('exit_code') == 0 else "❌"
        
        lines = [
            f"*Alert After Pro* {status_emoji}",
            "",
            f"🖥️ *Host:* `{data.get('hostname', 'unknown')}`",
            f"💻 *Command:* `{data.get('command', 'unknown')}`",
            f"⏱️ *Duration:* {data.get('duration', 'unknown')}",
            f"📊 *Exit Code:* {data.get('exit_code', 'unknown')}",
        ]
        
        if data.get('output'):
            output = data['output'][:500]
            lines.extend(["", "📋 *Output:*", f"```\n{output}\n```"])
        
        if data.get('error') and data.get('exit_code') != 0:
            error = data['error'][:300]
            lines.extend(["", "❌ *Error:*", f"```\n{error}\n```"])
        
        return '\n'.join(lines)