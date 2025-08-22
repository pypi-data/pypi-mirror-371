"""
Spimind日志记录库 - 专为脉冲神经网络设计的事件流日志系统
"""

from .core import SNNLogger
from .backends import TinyDBBackend

def init(project="spimind-sim", run_name=None, **kwargs):
    """
    初始化Spimind日志记录器
    
    Args:
        project (str): 项目名称
        run_name (str): 运行名称，如果为None则自动生成
        **kwargs: 传递给后端的具体参数
    
    Returns:
        SNNLogger: 日志记录器实例
    """
    backend_instance = TinyDBBackend(project, run_name, **kwargs)
    return SNNLogger(backend_instance)

__version__ = "0.1.0"
__all__ = ["init", "SNNLogger"]
