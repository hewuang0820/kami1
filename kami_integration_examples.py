#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
卡密验证系统集成示例
展示如何在不同场景下集成卡密验证功能
"""

import sys
import os
import time
import json
import logging
from typing import Dict, Any, Optional

# 导入验证工具库
try:
    from verification_utils import KamiVerifier, HardwareInfo, is_card_valid, verify_card
except ImportError:
    print("错误: 未能导入验证工具库")
    print("请确保verification_utils.py文件在当前目录")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('kami_verification.log')]
)
logger = logging.getLogger('kami_verification')


# 示例1: 简单的命令行应用程序启动保护
def example_app_startup_protection():
    """
    应用程序启动保护示例
    在程序启动时验证卡密，如果无效则退出
    """
    print("=" * 60)
    print("示例1: 应用程序启动保护")
    print("=" * 60)

    # 检查是否已验证
    if is_card_valid():
        print("卡密验证通过，正在启动程序...")
        print("程序已成功启动，可以开始使用了！")
        return True
    
    # 未验证，要求用户输入卡密
    print("首次使用本软件需要验证卡密")
    print("请联系供应商获取卡密")
    
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        key = input("\n请输入卡密: ").strip()
        if not key:
            print("错误: 卡密不能为空")
            continue
            
        print("正在验证卡密，请稍候...")
        result = verify_card(key)
        
        if result['success']:
            print("\n✅ 卡密验证成功!")
            print("软件已激活，感谢您的使用!")
            print("程序正在启动...")
            print("程序已成功启动，可以开始使用了！")
            return True
        else:
            attempts += 1
            remaining = max_attempts - attempts
            print(f"\n❌ 卡密验证失败: {result['message']}")
            if remaining > 0:
                print(f"您还有 {remaining} 次尝试机会")
            else:
                print("验证次数已用完，程序将退出")
                return False
    
    return False


# 示例2: 软件功能解锁
def example_feature_unlock():
    """
    软件功能解锁示例
    根据卡密类型解锁不同级别的功能
    """
    print("\n" + "=" * 60)
    print("示例2: 软件功能解锁")
    print("=" * 60)
    
    # 初始化验证器
    verifier = KamiVerifier()
    is_valid, data = verifier.is_verified()
    
    # 定义功能列表
    features = {
        "basic": ["文件读取", "基本编辑", "保存文件"],
        "standard": ["语法高亮", "自动补全", "主题切换"],
        "premium": ["智能建议", "代码分析", "团队协作", "云端同步"]
    }
    
    # 确定用户等级
    user_level = "无卡密"
    if is_valid and data and 'data' in data:
        card_type = data['data'].get('cardType', '')
        if "高级" in card_type:
            user_level = "premium"
        elif "标准" in card_type:
            user_level = "standard"
        elif "基础" in card_type:
            user_level = "basic"
    
    # 显示用户可用功能
    print(f"当前用户级别: {user_level}")
    print("可用功能:")
    
    available_features = []
    if user_level == "premium":
        available_features = features["basic"] + features["standard"] + features["premium"]
    elif user_level == "standard":
        available_features = features["basic"] + features["standard"]
    elif user_level == "basic":
        available_features = features["basic"]
    
    for feature in available_features:
        print(f"- {feature}")
    
    # 显示未解锁功能
    if user_level != "premium":
        print("\n升级到高级版可解锁以下功能:")
        for feature in features["premium"]:
            if feature not in available_features:
                print(f"- {feature}")
    
    if user_level == "无卡密":
        print("\n请购买卡密以解锁更多功能!")
        key = input("输入卡密立即升级(直接回车跳过): ")
        if key.strip():
            print("正在验证卡密...")
            result = verifier.verify_card_key(key)
            if result['success']:
                print("✅ 卡密验证成功，软件已升级!")
            else:
                print(f"❌ 卡密验证失败: {result['message']}")


# 示例3: 周期性校验
def example_periodic_verification():
    """
    周期性校验示例
    定期检查卡密是否依然有效，适用于订阅模式软件
    """
    print("\n" + "=" * 60)
    print("示例3: 周期性校验(模拟)")
    print("=" * 60)
    
    # 初始化验证器
    verifier = KamiVerifier()
    
    # 模拟软件运行
    print("软件正在运行...")
    
    # 模拟周期性检查3次
    for i in range(1, 4):
        print(f"\n[模拟] 第{i}次周期性检查 (假设间隔24小时)")
        
        # 检查卡密是否有效
        is_valid, data = verifier.is_verified()
        
        if is_valid:
            print("✅ 卡密验证通过，软件可以继续使用")
            
            # 显示卡密信息
            if data and 'data' in data:
                expiry_time = data['data'].get('expiryTime', '')
                if expiry_time:
                    print(f"卡密过期时间: {expiry_time[:10]}")
                    
                    # 如果剩余天数少于7天，显示提醒
                    try:
                        import datetime
                        expiry = datetime.datetime.fromisoformat(expiry_time)
                        now = datetime.datetime.now()
                        days_left = (expiry - now).days
                        
                        if days_left <= 7:
                            print(f"⚠️ 注意: 您的卡密将在 {days_left} 天后过期，请及时续费")
                    except:
                        pass
        else:
            print("❌ 卡密已过期或无效")
            print("请重新验证卡密以继续使用软件")
            break
        
        # 模拟时间流逝
        print("软件继续运行中...")
        time.sleep(1)  # 实际应用中是24小时


# 示例4: 绑定软件配置文件
def example_config_binding():
    """
    配置文件绑定示例
    将软件配置与硬件信息绑定，防止配置文件复制到其他设备使用
    """
    print("\n" + "=" * 60)
    print("示例4: 配置文件绑定")
    print("=" * 60)
    
    CONFIG_FILE = "software_config.json"
    
    # 获取硬件ID
    hardware_id = HardwareInfo.generate_hardware_id()
    print(f"当前设备硬件ID: {hardware_id}")
    
    # 检查配置文件是否存在
    if os.path.exists(CONFIG_FILE):
        # 读取配置文件
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            # 检查硬件ID是否匹配
            if config.get('hardware_id') == hardware_id:
                print("✅ 配置文件验证通过")
                print("软件配置:")
                for key, value in config.items():
                    if key != 'hardware_id':
                        print(f"- {key}: {value}")
            else:
                print("❌ 配置文件与当前设备不匹配")
                print("警告: 检测到可能的非法复制行为")
                print("配置文件将被重置")
                
                # 创建新的配置文件
                create_new_config(hardware_id)
        except:
            print("❌ 配置文件损坏")
            create_new_config(hardware_id)
    else:
        print("未发现配置文件，创建新配置...")
        create_new_config(hardware_id)


def create_new_config(hardware_id):
    """为示例4创建新的配置文件"""
    config = {
        'hardware_id': hardware_id,
        'theme': 'default',
        'language': 'zh_CN',
        'auto_save': True,
        'font_size': 12
    }
    
    with open("software_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ 新配置文件已创建")
    

# 示例5: 自定义验证参数
def example_custom_verification():
    """
    自定义验证参数示例
    使用不同的API和存储位置
    """
    print("\n" + "=" * 60)
    print("示例5: 自定义验证参数")
    print("=" * 60)
    
    # 创建自定义验证器
    custom_verifier = KamiVerifier(
        api_url='http://170.106.175.187/api/card-keys/verify',  # 你的公网 API 地址
        verification_file='custom_verification.bin',
        legacy_file='custom_verification.json'
    )
    
    print("使用自定义验证参数:")
    print(f"API地址: {custom_verifier.api_url}")
    print(f"验证文件: {custom_verifier.verification_file}")
    
    # 检查是否有效
    is_valid, data = custom_verifier.is_verified()
    if is_valid:
        print("✅ 自定义位置的验证文件有效")
    else:
        print("❌ 自定义位置未找到有效验证")
        print("需要进行验证...")


# 主函数
def main():
    print("\n欢迎使用卡密验证系统集成示例")
    print("本示例展示如何在不同场景下集成卡密验证功能\n")
    
    # 运行示例1: 应用程序启动保护
    if not example_app_startup_protection():
        print("应用程序启动保护验证失败，程序退出")
        return
    
    # 运行示例2: 软件功能解锁
    example_feature_unlock()
    
    # 运行示例3: 周期性校验
    example_periodic_verification()
    
    # 运行示例4: 绑定软件配置文件
    example_config_binding()
    
    # 运行示例5: 自定义验证参数
    example_custom_verification()
    
    print("\n" + "=" * 60)
    print("示例演示完成，感谢使用!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as e:
        logger.exception("运行示例时出错")
        print(f"运行示例时出错: {e}") 