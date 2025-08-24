import sys
import platform
from typing import Dict, Any


def get_system_info() -> Dict[str, Any]:
    """Get basic system information for debugging"""
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'python_version': sys.version,
        'python_executable': sys.executable
    }


def validate_config(config_data: Dict[str, Any]) -> Dict[str, str]:
    """Validate configuration and return any errors"""
    errors = {}
    enabled_notifiers = config_data.get('enabled_notifiers', [])
    
    for notifier in enabled_notifiers:
        if notifier == 'telegram':
            telegram_config = config_data.get('telegram', {})
            if not telegram_config.get('bot_token'):
                errors['telegram'] = "bot_token is required"
            elif not telegram_config.get('chat_id'):
                errors['telegram'] = "chat_id is required"
        
        elif notifier == 'ntfy':
            ntfy_config = config_data.get('ntfy', {})
            if not ntfy_config.get('topic'):
                errors['ntfy'] = "topic is required"
        
        elif notifier == 'dingding':
            dingding_config = config_data.get('dingding', {})
            if not dingding_config.get('webhook'):
                errors['dingding'] = "webhook is required"
        
        elif notifier == 'sms':
            sms_config = config_data.get('sms', {})
            required_fields = ['account_sid', 'auth_token', 'from_number', 'to_number']
            for field in required_fields:
                if not sms_config.get(field):
                    errors['sms'] = f"{field} is required"
                    break
        
        elif notifier == 'pushover':
            pushover_config = config_data.get('pushover', {})
            if not pushover_config.get('app_token'):
                errors['pushover'] = "app_token is required"
            elif not pushover_config.get('user_key'):
                errors['pushover'] = "user_key is required"
    
    return errors


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to a maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix