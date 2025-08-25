"""
Core command execution and monitoring functionality.
"""

import subprocess
import time
import signal
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime


class CommandRunner:
    """Executes commands and tracks their lifecycle."""
    
    def __init__(self, command: List[str], notifiers: Optional[List] = None):
        self.command = command
        self.notifiers = notifiers or []
        self.start_time = None
        self.end_time = None
        self.return_code = None
        self.pid = None
        self.process = None
        
    def run(self) -> int:
        """Execute the command and return its exit code."""
        self.start_time = datetime.now()
        command_str = ' '.join(self.command)
        
        try:
            print(f"🐚📯 shellhorn: Starting command: {command_str}")
            self._notify_start(command_str)
            
            # Execute the command
            self.process = subprocess.Popen(
                self.command,
                stdout=sys.stdout,
                stderr=sys.stderr,
                stdin=sys.stdin
            )
            self.pid = self.process.pid
            
            # Wait for completion
            self.return_code = self.process.wait()
            self.end_time = datetime.now()
            
            duration = (self.end_time - self.start_time).total_seconds()
            
            if self.return_code == 0:
                print(f"🐚📯 shellhorn: Command completed successfully in {duration:.2f}s")
                self._notify_success(command_str, duration)
            else:
                print(f"🐚📯 shellhorn: Command failed with exit code {self.return_code} after {duration:.2f}s")
                self._notify_failure(command_str, self.return_code, duration)
                
        except KeyboardInterrupt:
            print("🐚📯 shellhorn: Received interrupt signal")
            self._handle_interrupt(command_str)
            return 130
        except Exception as e:
            print(f"🐚📯 shellhorn: Unexpected error: {e}")
            self._notify_error(command_str, str(e))
            return 1
            
        return self.return_code
    
    def _notify_start(self, command: str):
        """Notify all registered notifiers about command start."""
        for notifier in self.notifiers:
            try:
                notifier.notify_start(command, self.pid)
            except Exception as e:
                print(f"🐚📯 shellhorn: Notification error: {e}")
    
    def _notify_success(self, command: str, duration: float):
        """Notify all registered notifiers about successful completion."""
        for notifier in self.notifiers:
            try:
                notifier.notify_success(command, duration, self.return_code)
            except Exception as e:
                print(f"🐚📯 shellhorn: Notification error: {e}")
    
    def _notify_failure(self, command: str, return_code: int, duration: float):
        """Notify all registered notifiers about command failure."""
        for notifier in self.notifiers:
            try:
                notifier.notify_failure(command, return_code, duration)
            except Exception as e:
                print(f"🐚📯 shellhorn: Notification error: {e}")
    
    def _notify_error(self, command: str, error: str):
        """Notify all registered notifiers about unexpected errors."""
        for notifier in self.notifiers:
            try:
                notifier.notify_error(command, error)
            except Exception as e:
                print(f"🐚📯 shellhorn: Notification error: {e}")
    
    def _handle_interrupt(self, command: str):
        """Handle keyboard interrupt gracefully."""
        if self.process:
            print("🐚📯 shellhorn: Terminating process...")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("🐚📯 shellhorn: Force killing process...")
                self.process.kill()
        
        duration = (datetime.now() - self.start_time).total_seconds()
        for notifier in self.notifiers:
            try:
                notifier.notify_interrupted(command, duration)
            except Exception as e:
                print(f"🐚📯 shellhorn: Notification error: {e}")


class BaseNotifier:
    """Base class for all notifiers."""
    
    def notify_start(self, command: str, pid: int):
        """Called when command starts."""
        pass
    
    def notify_success(self, command: str, duration: float, return_code: int):
        """Called when command completes successfully."""
        pass
    
    def notify_failure(self, command: str, return_code: int, duration: float):
        """Called when command fails."""
        pass
    
    def notify_error(self, command: str, error: str):
        """Called when an unexpected error occurs."""
        pass
    
    def notify_interrupted(self, command: str, duration: float):
        """Called when command is interrupted."""
        pass