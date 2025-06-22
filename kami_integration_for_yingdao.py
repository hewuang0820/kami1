#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
影刀RPA卡密验证集成示例
展示如何在影刀RPA中集成卡密验证功能
"""

import sys
import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog

# 导入验证工具库
try:
    from verification_utils import KamiVerifier, is_card_valid, verify_card
except ImportError:
    print("错误: 未能导入验证工具库")
    print("请确保verification_utils.py文件在当前目录")
    sys.exit(1)

class KamiVerificationForYingdao:
    """影刀RPA卡密验证集成类"""
    
    def __init__(self, verification_file='verification.bin'):
        """初始化验证器"""
        self.verifier = KamiVerifier(verification_file=verification_file)
        
    def check_verification(self):
        """检查是否已有有效卡密"""
        return is_card_valid()
    
    def verify_with_gui(self):
        """使用GUI界面验证卡密"""
        # 创建一个临时的Tkinter窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 检查是否已有有效卡密
        if self.check_verification():
            messagebox.showinfo("卡密验证", "卡密验证成功，可以继续使用")
            root.destroy()
            return True
        
        # 显示卡密输入对话框
        key = simpledialog.askstring("卡密验证", "请输入卡密:", parent=root)
        
        if not key:
            messagebox.showerror("错误", "卡密不能为空")
            root.destroy()
            return False
        
        # 验证卡密
        result = verify_card(key)
        
        if result['success']:
            messagebox.showinfo("成功", "卡密验证成功，可以继续使用")
            root.destroy()
            return True
        else:
            messagebox.showerror("错误", f"卡密验证失败: {result['message']}")
            root.destroy()
            return False
    
    def verify_with_input_output(self, key):
        """使用输入输出方式验证卡密，适用于影刀直接调用"""
        if not key:
            return json.dumps({
                'success': False,
                'message': '卡密不能为空'
            })
        
        # 验证卡密
        result = verify_card(key)
        return json.dumps(result)

# 影刀调用入口函数
def verify_kami_for_yingdao(key=None):
    """
    影刀RPA调用的入口函数
    
    参数:
        key (str, 可选): 卡密字符串，如果为None则使用GUI方式验证
        
    返回:
        bool 或 str: 如果是GUI方式，返回验证结果布尔值；如果是输入输出方式，返回JSON字符串
    """
    verifier = KamiVerificationForYingdao()
    
    # 如果已有有效卡密，直接返回成功
    if verifier.check_verification():
        if key is None:
            return True
        else:
            return json.dumps({
                'success': True,
                'message': '设备已有有效卡密'
            })
    
    # 根据是否提供卡密决定验证方式
    if key is None:
        return verifier.verify_with_gui()
    else:
        return verifier.verify_with_input_output(key)

# 命令行测试入口
if __name__ == "__main__":
    # 如果有命令行参数，使用参数作为卡密
    if len(sys.argv) > 1:
        result = verify_kami_for_yingdao(sys.argv[1])
        print(result)
    else:
        # 否则使用GUI方式验证
        result = verify_kami_for_yingdao()
        print(f"验证结果: {'成功' if result else '失败'}") 