#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
卡密验证工具
用于验证卡密是否有效
"""

import sys
import json

# 检查是否安装了requests库
try:
    import requests
except ImportError:
    print("错误: 未安装requests库")
    print("请运行以下命令安装:")
    print("pip install requests")
    print("\n如果您使用的是Windows系统，可能需要以管理员身份运行命令提示符")
    sys.exit(1)

def verify_card_key(key, user_identifier='', api_url='http://170.106.175.187/api/card-keys/verify'):
    """
    验证卡密是否有效
    
    参数:
        key (str): 要验证的卡密
        user_identifier (str, 可选): 用户标识符，用于记录谁使用了卡密
        api_url (str, 可选): API地址，默认为http://170.106.175.187/api/card-keys/verify
        
    返回:
        dict: 包含验证结果的字典
    """
    try:
        # 发送POST请求到API
        response = requests.post(
            api_url,
            json={'key': key, 'userIdentifier': user_identifier},
            timeout=10  # 10秒超时
        )
        
        # 检查HTTP状态码
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False, 
                'message': f'API错误: HTTP {response.status_code}'
            }
            
    except requests.exceptions.Timeout:
        return {'success': False, 'message': '连接超时，请检查网络'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'message': '连接失败，请检查网络或API地址'}
    except json.JSONDecodeError:
        return {'success': False, 'message': 'API返回的数据格式错误'}
    except Exception as e:
        return {'success': False, 'message': f'未知错误: {str(e)}'}

def print_result(result):
    """打印验证结果"""
    print("\n===== 验证结果 =====")
    if result['success']:
        print("✅ 卡密验证成功!")
        print(f"卡密: {result['data'].get('key', '未知')}")
        print(f"类型: {result['data'].get('cardType', '未知')}")
        print(f"有效期: {result['data'].get('validDays', '未知')}天")
        
        # 格式化过期时间
        expiry_time = result['data'].get('expiryTime')
        if expiry_time:
            print(f"过期时间: {expiry_time[:10]}")  # 只显示日期部分
    else:
        print("❌ 卡密验证失败!")
        print(f"原因: {result['message']}")
    print("===================\n")

def main():
    """主函数"""
    print("==== 卡密验证工具 ====")
    print("此工具用于验证卡密是否有效")
    
    # 获取用户输入
    key = input("请输入卡密: ").strip()
    if not key:
        print("错误: 卡密不能为空")
        return
    
    user_id = input("请输入用户标识(可选): ").strip()
    
    print("\n正在验证卡密，请稍候...")
    result = verify_card_key(key, user_id)
    print_result(result)
    
    # 询问用户是否继续
    while input("是否继续验证其他卡密? (y/n): ").lower() == 'y':
        key = input("请输入卡密: ").strip()
        if not key:
            print("错误: 卡密不能为空")
            continue
        
        user_id = input("请输入用户标识(可选): ").strip()
        
        print("\n正在验证卡密，请稍候...")
        result = verify_card_key(key, user_id)
        print_result(result)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断")
    except Exception as e:
        print(f"\n程序出错: {str(e)}")
    finally:
        print("\n感谢使用卡密验证工具!") 