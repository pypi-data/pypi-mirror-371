from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseNotifier(ABC):
    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def send(self, data: Dict[str, Any]) -> bool:
        pass
    
    def format_message(self, data: Dict[str, Any]) -> str:
        lines = [
            f"🖥️ Host: {data.get('hostname', 'unknown')}",
            f"📍 Status: {data.get('status', 'unknown')}",
            f"⏱️ Duration: {data.get('duration', 'unknown')}",
            f"💻 Command: {data.get('command', 'unknown')}",
        ]
        
        if data.get('output'):
            lines.append(f"\n📋 Output:\n{data['output']}")
        
        if data.get('error'):
            lines.append(f"\n❌ Error:\n{data['error']}")
        
        return '\n'.join(lines)