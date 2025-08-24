from typing import Dict, Any
from .base import BaseNotifier


class SMSNotifier(BaseNotifier):
    def send(self, data: Dict[str, Any]) -> bool:
        sms_config = self.config.get('sms', {})
        provider = sms_config.get('provider', 'twilio')
        
        if provider == 'twilio':
            return self._send_twilio(data, sms_config)
        else:
            raise ValueError(f"Unsupported SMS provider: {provider}")
    
    def _send_twilio(self, data: Dict[str, Any], config: Dict[str, Any]) -> bool:
        try:
            from twilio.rest import Client
        except ImportError:
            raise ImportError("Twilio library not installed. Run: pip install twilio")
        
        account_sid = config.get('account_sid')
        auth_token = config.get('auth_token')
        from_number = config.get('from_number')
        to_number = config.get('to_number')
        
        if not all([account_sid, auth_token, from_number, to_number]):
            raise ValueError("Twilio credentials are incomplete")
        
        client = Client(account_sid, auth_token)
        
        status_emoji = "✅" if data.get('exit_code') == 0 else "❌"
        
        message_body = self.format_sms_message(data)
        
        try:
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=to_number
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to send SMS via Twilio: {e}")
    
    def format_sms_message(self, data: Dict[str, Any]) -> str:
        status = "Success ✅" if data.get('exit_code') == 0 else "Failed ❌"
        
        lines = [
            f"Alert After Pro {status}",
            f"Host: {data.get('hostname', 'unknown')}",
            f"Cmd: {data.get('command', 'unknown')[:50]}",
            f"Time: {data.get('duration', 'unknown')}",
            f"Code: {data.get('exit_code', 'unknown')}"
        ]
        
        if data.get('error') and data.get('exit_code') != 0:
            lines.append(f"Error: {data['error'][:50]}...")
        
        return '\n'.join(lines)