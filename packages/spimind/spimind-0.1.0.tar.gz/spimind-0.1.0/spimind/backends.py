"""
SNN日志后端存储模块
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path
from tinydb import TinyDB, Query
from .core import BackendBase


class TinyDBBackend(BackendBase):
    """TinyDB数据库后端存储"""
    
    def __init__(self, project: str, run_name: Optional[str] = None,
                 db_path: str = "logs/spimind.json", **kwargs):
        """
        初始化TinyDB后端
        
        Args:
            project: 项目名称
            run_name: 运行名称
            db_path: 数据库文件路径
        """
        self.project = project
        self.run_name = run_name or f"run_{int(time.time())}"
        
        # 确保目录存在
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self.db = TinyDB(db_path)
        self.events_table = self.db.table('events')
        self.sessions_table = self.db.table('sessions')
        
    def write_event(self, event_data: Dict[str, Any]) -> None:
        """写入事件到TinyDB数据库"""
        # 插入事件记录
        self.events_table.insert(event_data)
        
        # 如果是会话开始事件，插入会话记录
        if event_data.get('event') == 'session_start':
            session_data = {
                'session_id': event_data.get('session_id'),
                'project': self.project,
                'run_name': self.run_name,
                'start_time': event_data.get('time'),
                'end_time': None,
                'duration': None
            }
            self.sessions_table.insert(session_data)
        
        # 如果是会话结束事件，更新会话记录
        elif event_data.get('event') == 'session_end':
            Session = Query()
            self.sessions_table.update({
                'end_time': event_data.get('time'),
                'duration': event_data.get('duration')
            }, Session.session_id == event_data.get('session_id'))
    
    def close(self) -> None:
        """关闭数据库连接"""
        if hasattr(self, 'db'):
            self.db.close()
