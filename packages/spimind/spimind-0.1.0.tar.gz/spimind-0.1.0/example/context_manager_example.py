"""
Spimind上下文管理器示例
"""

import spimind
import time

def main():
    """上下文管理器示例"""
    print("=== Spimind上下文管理器示例 ===")
    
    with spimind.init(project="example", run_name="context_demo") as logger:
        print("进入上下文管理器...")
        
        # 模拟Spimind推理过程
        for step in range(3):
            logger.log_event(
                event="inference_step",
                event_time=step * 0.001,
                step=step,
                batch_size=1
            )
            
            # 模拟神经元发放
            for i in range(2):
                logger.log_event(
                    event="spike",
                    event_time=step * 0.001,
                    neuron=f"ctx_neuron_{i}",
                    step=step
                )
            
            time.sleep(0.01)
        
        print("即将退出上下文管理器...")
    
    print("上下文管理器示例完成！")

if __name__ == "__main__":
    main()
