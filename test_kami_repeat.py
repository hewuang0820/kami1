#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
卡密重复使用测试脚本
验证已验证过的卡密可以重复使用
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def test_repeat_verification():
    print("=== 卡密重复使用测试 ===")
    
    try:
        from yingdao_kami_integration import (
            初始化, 单码, 检查登录状态, 退出, 
            检查本地验证, 调试验证文件, 清理验证文件
        )
        
        # 初始化系统
        print("1. 初始化系统...")
        if not 初始化():
            print("❌ 系统初始化失败")
            return
        print("✅ 系统初始化成功")
        
        # 获取测试卡密
        test_key = input("\n请输入测试卡密: ").strip()
        if not test_key:
            print("❌ 卡密不能为空")
            return
        
        print(f"\n=== 第一次验证卡密: {test_key} ===")
        
        # 第一次验证
        result1 = 单码(test_key)
        print(f"第一次验证结果: {result1}")
        
        if not 检查登录状态():
            print("❌ 第一次验证失败")
            return
        
        print("✅ 第一次验证成功")
        
        # 退出登录
        print("\n2. 退出登录...")
        退出()
        
        # 检查本地验证状态
        print("\n3. 检查本地验证状态...")
        local_check = 检查本地验证()
        print(f"本地验证状态: {local_check}")
        
        # 调试验证文件
        print("\n4. 调试验证文件...")
        debug_info = 调试验证文件()
        print(debug_info)
        
        print(f"\n=== 第二次验证同一卡密: {test_key} ===")
        
        # 第二次验证同一卡密
        result2 = 单码(test_key)
        print(f"第二次验证结果: {result2}")
        
        if 检查登录状态():
            print("✅ 第二次验证成功 - 卡密重复使用功能正常")
        else:
            print("❌ 第二次验证失败 - 卡密重复使用功能异常")
        
        # 退出登录
        退出()
        
        print(f"\n=== 测试不同卡密 ===")
        
        # 测试不同卡密
        different_key = input("\n请输入一个不同的卡密进行测试（可以是无效的）: ").strip()
        if different_key and different_key != test_key:
            result3 = 单码(different_key)
            print(f"不同卡密验证结果: {result3}")
            
            if 检查登录状态():
                print("✅ 不同卡密验证成功")
                退出()
            else:
                print("❌ 不同卡密验证失败（这是正常的，如果卡密无效）")
        
        print(f"\n=== 再次验证原卡密: {test_key} ===")
        
        # 再次验证原卡密
        result4 = 单码(test_key)
        print(f"再次验证原卡密结果: {result4}")
        
        if 检查登录状态():
            print("✅ 原卡密仍然可以使用 - 功能完全正常")
            退出()
        else:
            print("❌ 原卡密无法使用 - 需要检查问题")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("这个脚本将测试卡密重复使用功能")
    print("确保您有一个有效的卡密进行测试")
    
    choice = input("\n是否开始测试？(y/n): ").lower()
    if choice == 'y':
        test_repeat_verification()
    else:
        print("测试已取消")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...") 