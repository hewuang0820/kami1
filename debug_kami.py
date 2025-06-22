#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
卡密验证系统调试工具
用于诊断和解决验证问题
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def main():
    print("=== 卡密验证系统调试工具 ===")
    
    try:
        # 导入验证模块
        from yingdao_kami_integration import (
            初始化, 调试验证文件, 清理验证文件, 
            检查本地验证, 单码, 检查登录状态
        )
        
        print("✅ 模块导入成功")
        
        # 初始化系统
        print("\n1. 初始化系统...")
        if 初始化():
            print("✅ 系统初始化成功")
        else:
            print("❌ 系统初始化失败")
            return
        
        # 调试验证文件
        print("\n2. 调试验证文件...")
        debug_info = 调试验证文件()
        print(debug_info)
        
        # 检查本地验证
        print("\n3. 检查本地验证状态...")
        local_check = 检查本地验证()
        print(f"验证结果: {local_check}")
        
        # 根据情况提供建议
        if local_check['valid']:
            print("\n✅ 本地验证有效，可以正常使用")
        else:
            print("\n❌ 本地验证无效")
            
            # 询问用户是否要清理验证文件
            choice = input("\n是否要清理验证文件并重新验证？(y/n): ").lower()
            if choice == 'y':
                print("\n4. 清理验证文件...")
                clean_result = 清理验证文件()
                print(clean_result)
                
                # 重新验证
                test_key = input("\n请输入卡密进行重新验证: ").strip()
                if test_key:
                    print("正在验证卡密...")
                    result = 单码(test_key)
                    print(f"验证结果: {result}")
                    
                    if 检查登录状态():
                        print("✅ 验证成功，系统已正常工作")
                    else:
                        print("❌ 验证失败")
        
        print("\n=== 调试完成 ===")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保 yingdao_kami_integration.py 文件在当前目录")
    except Exception as e:
        print(f"❌ 调试过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\n按回车键退出...") 