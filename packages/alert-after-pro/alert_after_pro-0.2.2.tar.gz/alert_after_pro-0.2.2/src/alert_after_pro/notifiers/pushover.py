import requests
from typing import Dict, Any
from .base import BaseNotifier


class PushoverNotifier(BaseNotifier):
    def send(self, data: Dict[str, Any]) -> bool:
        pushover_config = self.config.get('pushover', {})
        app_token = pushover_config.get('app_token')
        user_key = pushover_config.get('user_key')
        
        if not app_token or not user_key:
            raise ValueError("Pushover app_token and user_key are required")
        
        url = "https://api.pushover.net/1/messages.json"
        
        status_emoji = "✅" if data.get('exit_code') == 0 else "❌"
        title = f"Command {status_emoji}: {data.get('command', 'unknown')[:100]}"
        
        message = self.format_pushover_message(data)
        
        priority = 0 if data.get('exit_code') == 0 else 1
        
        payload = {
            'token': app_token,
            'user': user_key,
            'title': title,
            'message': message,
            'priority': priority,
            'sound': 'pushover' if data.get('exit_code') == 0 else 'falling'
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') != 1:
                raise Exception(f"Pushover API error: {result}")
            
            return True
        except Exception as e:
            raise Exception(f"Failed to send Pushover notification: {e}")
    
    def format_pushover_message(self, data: Dict[str, Any]) -> str:
        lines = [
            f"Host: {data.get('hostname', 'unknown')}",
            f"Duration: {data.get('duration', 'unknown')}",
            f"Exit Code: {data.get('exit_code', 'unknown')}"
        ]
        
        if data.get('output'):
            lines.append(f"\nOutput:\n{data['output'][:500]}")
        
        if data.get('error') and data.get('exit_code') != 0:
            lines.append(f"\nError:\n{data['error'][:300]}")
        
        return '\n'.join(lines)