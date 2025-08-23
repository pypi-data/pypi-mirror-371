#!/usr/bin/env python3
import sys
import subprocess
import time
import socket
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import argparse
import signal

from .config import Config, setup_wizard
from .notifiers import get_notifier


class CommandRunner:
    def __init__(self):
        self.config = Config()
        self.start_time = None
        self.end_time = None
        self.command = None
        self.exit_code = None
        self.output = None
        self.error = None
        
    def run_command(self, command: List[str]) -> int:
        self.command = ' '.join(command)
        self.start_time = datetime.now()
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True if len(command) == 1 else False
            )
            
            def signal_handler(signum, frame):
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                sys.exit(130)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            self.output, self.error = process.communicate()
            self.exit_code = process.returncode
            
        except Exception as e:
            self.error = str(e)
            self.exit_code = 1
            
        self.end_time = datetime.now()
        return self.exit_code
    
    def get_duration(self) -> str:
        if not self.start_time or not self.end_time:
            return "unknown"
        
        duration = self.end_time - self.start_time
        total_seconds = int(duration.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def send_notifications(self):
        if not self.config.is_configured():
            print("\n⚠️  Alert After Pro is not configured. Run 'aa --setup' to configure notifications.")
            return
        
        hostname = socket.gethostname()
        status = "✅ Success" if self.exit_code == 0 else f"❌ Failed (code: {self.exit_code})"
        
        message_data = {
            'command': self.command,
            'hostname': hostname,
            'status': status,
            'duration': self.get_duration(),
            'exit_code': self.exit_code,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else 'unknown',
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'unknown'
        }
        
        if self.config.get('capture_output', False) and self.output:
            message_data['output'] = self.output[:1000]
        
        if self.error and self.exit_code != 0:
            message_data['error'] = self.error[:500]
        
        enabled_notifiers = self.config.get('enabled_notifiers', [])
        
        for notifier_name in enabled_notifiers:
            try:
                notifier_class = get_notifier(notifier_name)
                if notifier_class:
                    notifier = notifier_class(self.config)
                    notifier.send(message_data)
                    print(f"✓ Notification sent via {notifier_name}")
            except Exception as e:
                print(f"✗ Failed to send {notifier_name} notification: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Alert After Pro - Get notified when commands complete',
        usage='aa [options] <command>'
    )
    
    parser.add_argument('--setup', action='store_true', 
                       help='Run the configuration wizard')
    parser.add_argument('--test', action='store_true',
                       help='Send a test notification')
    parser.add_argument('--silent', action='store_true',
                       help='Suppress notification output')
    parser.add_argument('command', nargs=argparse.REMAINDER,
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.setup:
        setup_wizard()
        return
    
    runner = CommandRunner()
    
    if args.test:
        runner.command = "Test notification from Alert After Pro"
        runner.start_time = datetime.now()
        runner.end_time = datetime.now()
        runner.exit_code = 0
        runner.send_notifications()
        return
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    exit_code = runner.run_command(args.command)
    
    if runner.output:
        print(runner.output, end='')
    if runner.error:
        print(runner.error, end='', file=sys.stderr)
    
    if not args.silent:
        runner.send_notifications()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()