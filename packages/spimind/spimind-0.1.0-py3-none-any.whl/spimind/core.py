"""
SNN日志记录器核心模块
"""

import time
import uuid
from typing import Dict, Any, List, Callable, Optional
from abc import ABC, abstractmethod


class BackendBase(ABC):
    """后端存储基类"""
    
    @abstractmethod
    def write_event(self, event_data: Dict[str, Any]) -> None:
        """写入事件数据"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """关闭后端连接"""
        pass


class SNNLogger:
    """SNN事件流日志记录器"""
    
    def __init__(self, backend: BackendBase):
        """
        初始化日志记录器
        
        Args:
            backend: 后端存储实例
        """
        self.backend = backend
        self.hooks: List[Callable] = []
        self.session_id = str(uuid.uuid4())
        self.start_time = time.time()
        
        # 记录会话开始事件
        self.log_event(
            event="session_start",
            event_time=self.start_time,
            session_id=self.session_id
        )
    
    def log_event(self, event: str, event_time: float, **kwargs) -> None:
        """
        记录事件
        
        Args:
            event (str): 事件类型
            event_time (float): 事件时间戳
            **kwargs: 事件相关数据
        """
        event_data = {
            "event": event,
            "time": event_time,
            "session_id": self.session_id,
            "timestamp": time.time(),
            **kwargs
        }
        
        # 执行所有注册的hook
        for hook in self.hooks:
            try:
                hook(event_data)
            except Exception as e:
                print(f"Hook执行错误: {e}")
        
        # 写入后端
        self.backend.write_event(event_data)
    
    def add_hook(self, hook_func: Callable[[Dict[str, Any]], None]) -> None:
        """
        添加事件处理hook
        
        Args:
            hook_func: 处理事件的函数，接收事件数据字典
        """
        self.hooks.append(hook_func)
    
    def remove_hook(self, hook_func: Callable[[Dict[str, Any]], None]) -> None:
        """
        移除事件处理hook
        
        Args:
            hook_func: 要移除的hook函数
        """
        if hook_func in self.hooks:
            self.hooks.remove(hook_func)
    
    def close(self) -> None:
        """关闭日志记录器"""
        end_time = time.time()
        self.log_event(
            event="session_end",
            event_time=end_time,
            session_id=self.session_id,
            duration=end_time - self.start_time
        )
        self.backend.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
