import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from typing import Dict, Any
from .base import BaseNotifier


class DingDingNotifier(BaseNotifier):
    def send(self, data: Dict[str, Any]) -> bool:
        dingding_config = self.config.get('dingding', {})
        webhook = dingding_config.get('webhook')
        secret = dingding_config.get('secret')
        
        if not webhook:
            raise ValueError("DingDing webhook URL is required")
        
        url = webhook
        
        if secret:
            timestamp = str(round(time.time() * 1000))
            sign = self._calculate_sign(timestamp, secret)
            url = f"{webhook}&timestamp={timestamp}&sign={sign}"
        
        status_emoji = "✅" if data.get('exit_code') == 0 else "❌"
        
        content = self.format_dingding_message(data)
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"命令执行完成 {status_emoji}",
                "text": content
            },
            "at": {
                "isAtAll": False
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('errcode') != 0:
                raise Exception(f"DingDing API error: {result.get('errmsg')}")
            
            return True
        except Exception as e:
            raise Exception(f"Failed to send DingDing notification: {e}")
    
    def _calculate_sign(self, timestamp: str, secret: str) -> str:
        secret_enc = secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign
    
    def format_dingding_message(self, data: Dict[str, Any]) -> str:
        status = "成功 ✅" if data.get('exit_code') == 0 else "失败 ❌"
        
        lines = [
            f"## Alert After Pro 通知",
            "",
            f"**状态**: {status}",
            f"**主机**: {data.get('hostname', '未知')}",
            f"**命令**: `{data.get('command', '未知')}`",
            f"**耗时**: {data.get('duration', '未知')}",
            f"**退出码**: {data.get('exit_code', '未知')}",
            f"**开始时间**: {data.get('start_time', '未知')}",
            f"**结束时间**: {data.get('end_time', '未知')}"
        ]
        
        if data.get('output'):
            output = data['output'][:300]
            lines.extend(["", "**输出**:", f"```\n{output}\n```"])
        
        if data.get('error') and data.get('exit_code') != 0:
            error = data['error'][:300]
            lines.extend(["", "**错误**:", f"```\n{error}\n```"])
        
        return '\n'.join(lines)