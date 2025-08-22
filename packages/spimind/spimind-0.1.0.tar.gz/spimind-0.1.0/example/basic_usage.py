"""
Spimind基本使用示例
"""

import spimind
import time
import random

def main():
    """基本使用示例"""
    print("=== Spimind基本使用示例 ===")
    
    # 初始化日志记录器
    logger = spimind.init(
        project="example",
        run_name="basic_demo"
    )
    
    # 模拟神经元发放事件
    for t in range(10):
        # 模拟多个神经元的发放
        for neuron_id in range(5):
            if random.random() > 0.7:  # 30%概率发放
                logger.log_event(
                    event="spike",
                    event_time=t * 0.001,  # 1ms时间步
                    neuron=f"LIF_{neuron_id}",
                    layer="hidden1"
                )
        
        # 模拟权重更新
        if t % 3 == 0:
            logger.log_event(
                event="weight_update",
                event_time=t * 0.001,
                src="LIF_1",
                dst="LIF_3",
                delta_w=random.uniform(-0.1, 0.1)
            )
        
        # 模拟能量消耗
        logger.log_event(
            event="energy_consumption",
            event_time=t * 0.001,
            neuron="LIF_2",
            joules=random.uniform(0.0001, 0.0005)
        )
        
        time.sleep(0.01)  # 模拟计算时间
    
    logger.close()
    print("示例完成！日志已保存到 logs/spimind.json")

if __name__ == "__main__":
    main()
