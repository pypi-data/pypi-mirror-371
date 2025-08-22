"""
Spimind Hook功能示例
"""

import spimind
import time
import random

def main():
    """Hook功能示例"""
    print("=== Spimind Hook功能示例 ===")
    
    # 定义hook函数
    spike_count = 0
    def spike_monitor(event_data):
        nonlocal spike_count
        if event_data['event'] == 'spike':
            spike_count += 1
            print(f"🔴 检测到发放: {event_data['neuron']} @ {event_data['time']:.3f}s")
    
    def energy_monitor(event_data):
        if event_data['event'] == 'energy_consumption':
            print(f"⚡ 能量消耗: {event_data['joules']:.6f}J @ {event_data['time']:.3f}s")
    
    # 初始化带hook的日志记录器
    logger = spimind.init(
        project="example",
        run_name="hook_demo"
    )
    
    # 添加hook
    logger.add_hook(spike_monitor)
    logger.add_hook(energy_monitor)
    
    # 模拟事件
    for t in range(5):
        # 随机发放
        for neuron_id in range(3):
            if random.random() > 0.5:
                logger.log_event(
                    event="spike",
                    event_time=t * 0.001,
                    neuron=f"neuron_{neuron_id}",
                    layer="test"
                )
        
        # 能量消耗
        logger.log_event(
            event="energy_consumption",
            event_time=t * 0.001,
            neuron="neuron_1",
            joules=random.uniform(0.0001, 0.0003)
        )
        
        time.sleep(0.02)
    
    logger.close()
    print(f"总共检测到 {spike_count} 个发放事件")

if __name__ == "__main__":
    main()
