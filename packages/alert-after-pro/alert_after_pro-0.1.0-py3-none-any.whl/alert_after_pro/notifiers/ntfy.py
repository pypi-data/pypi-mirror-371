import requests
import base64
from typing import Dict, Any
from .base import BaseNotifier


class NtfyNotifier(BaseNotifier):
    def send(self, data: Dict[str, Any]) -> bool:
        ntfy_config = self.config.get('ntfy', {})
        server = ntfy_config.get('server', 'https://ntfy.sh')
        topic = ntfy_config.get('topic')
        
        if not topic:
            raise ValueError("Ntfy topic is required")
        
        url = f"{server}/{topic}"
        
        status_emoji = "✅" if data.get('exit_code') == 0 else "❌"
        title = f"Command {status_emoji}: {data.get('command', 'unknown')[:50]}"
        
        message_parts = [
            f"Host: {data.get('hostname', 'unknown')}",
            f"Duration: {data.get('duration', 'unknown')}",
            f"Exit Code: {data.get('exit_code', 'unknown')}"
        ]
        
        if data.get('output'):
            message_parts.append(f"\nOutput: {data['output'][:200]}...")
        
        if data.get('error') and data.get('exit_code') != 0:
            message_parts.append(f"\nError: {data['error'][:200]}...")
        
        message = '\n'.join(message_parts)
        
        headers = {
            'Priority': '3' if data.get('exit_code') == 0 else '4',
            'Tags': 'computer,aa',
            'Content-Type': 'text/plain; charset=utf-8'
        }
        
        # Encode title properly for HTTP headers
        title_encoded = title.encode('ascii', 'ignore').decode('ascii')
        headers['Title'] = title_encoded
        
        username = ntfy_config.get('username')
        password = ntfy_config.get('password')
        
        if username and password:
            auth = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers['Authorization'] = f'Basic {auth}'
        
        try:
            response = requests.post(
                url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            raise Exception(f"Failed to send Ntfy notification: {e}")