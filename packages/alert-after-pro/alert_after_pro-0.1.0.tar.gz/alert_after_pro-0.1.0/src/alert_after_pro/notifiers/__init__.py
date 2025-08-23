from typing import Optional, Type
from .base import BaseNotifier
from .telegram import TelegramNotifier
from .ntfy import NtfyNotifier
from .dingding import DingDingNotifier
from .sms import SMSNotifier
from .pushover import PushoverNotifier


NOTIFIERS = {
    'telegram': TelegramNotifier,
    'ntfy': NtfyNotifier,
    'dingding': DingDingNotifier,
    'sms': SMSNotifier,
    'pushover': PushoverNotifier
}


def get_notifier(name: str) -> Optional[Type[BaseNotifier]]:
    return NOTIFIERS.get(name)