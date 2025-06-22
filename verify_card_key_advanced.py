#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高级卡密验证工具
- 支持硬件绑定
- 支持验证文件加密
- 防止卡密文件复制到其他计算机使用
"""

import sys
import json
import os
import platform
import uuid
import subprocess
import base64
import hashlib
import datetime
from typing import Dict, Any, Optional, Tuple, Union

# pyright: reportOptionalMemberAccess=none, reportOptionalSubscript=none

# 检查是否安装了必要的库
try:
    import requests
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("错误: 未安装必要的库")
    print("请运行以下命令安装:")
    print("pip install requests cryptography")
    print("\n如果您使用的是Windows系统，可能需要以管理员身份运行命令提示符")
    sys.exit(1)

# 配置
API_URL = 'http://170.106.175.187/api/card-keys/verify'
VERIFICATION_FILE = 'verification.bin'  # 加密的验证文件
LEGACY_VERIFICATION_FILE = 'verification.json'  # 旧版明文验证文件
SALT = b'kami_verification_system_salt'  # 盐值，用于密钥派生


class HardwareInfo:
    """用于获取系统硬件信息"""
    
    @staticmethod
    def get_cpu_id() -> str:
        """获取CPU ID"""
        if platform.system() == "Windows":
            try:
                # Windows下获取CPU ID
                output = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode()
                return output.strip().split('\n')[1].strip()
            except:
                pass
        elif platform.system() == "Linux":
            try:
                # Linux下获取CPU ID
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('serial') or line.startswith('Serial'):
                            return line.strip().split(':')[1].strip()
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                # macOS下获取CPU ID
                output = subprocess.check_output("ioreg -l | grep IOPlatformSerialNumber", shell=True).decode()
                return output.strip().split('=')[1].strip().replace('"', '')
            except:
                pass
        
        # 如果无法获取特定ID，使用更通用的方法
        return platform.processor() + platform.machine()
    
    @staticmethod
    def get_disk_serial() -> str:
        """获取硬盘序列号"""
        if platform.system() == "Windows":
            try:
                # Windows下获取第一个硬盘序列号
                output = subprocess.check_output("wmic diskdrive get SerialNumber", shell=True).decode()
                serial = output.strip().split('\n')[1].strip()
                return serial if serial and serial != "" else str(uuid.getnode())
            except:
                pass
        elif platform.system() == "Linux":
            try:
                # Linux下尝试获取硬盘序列号
                output = subprocess.check_output("lsblk -d -o name,serial | grep -v loop", shell=True).decode()
                return output.strip().split('\n')[1].strip()
            except:
                pass
        # 如果无法获取，返回MAC地址的hash
        return str(uuid.getnode())
    
    @staticmethod
    def get_motherboard_serial() -> str:
        """获取主板序列号"""
        if platform.system() == "Windows":
            try:
                # Windows下获取主板序列号
                output = subprocess.check_output("wmic baseboard get SerialNumber", shell=True).decode()
                return output.strip().split('\n')[1].strip()
            except:
                pass
        elif platform.system() == "Linux":
            try:
                # Linux下尝试获取主板序列号
                output = subprocess.check_output("dmidecode -s baseboard-serial-number", shell=True).decode()
                return output.strip()
            except:
                pass
        # 如果无法获取特定序列号，使用计算机名称和当前用户名
        return platform.node() + os.getlogin()
    
    @staticmethod
    def generate_hardware_id() -> str:
        """生成唯一的硬件标识符"""
        cpu_id = HardwareInfo.get_cpu_id()
        disk_serial = HardwareInfo.get_disk_serial()
        motherboard_serial = HardwareInfo.get_motherboard_serial()
        
        # 组合硬件信息并生成一个哈希值作为唯一标识符
        hardware_info = f"{cpu_id}|{disk_serial}|{motherboard_serial}"
        hardware_hash = hashlib.sha256(hardware_info.encode()).hexdigest()
        
        return hardware_hash


class Encryption:
    """处理加密和解密操作"""
    
    @staticmethod
    def get_key(hardware_id: str) -> bytes:
        """从硬件ID生成加密密钥"""
        # 使用硬件ID和盐值派生一个密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(hardware_id.encode()))
        return key
    
    @staticmethod
    def encrypt_data(data: Dict[str, Any], hardware_id: str) -> bytes:
        """加密数据"""
        # 将数据转换为JSON字符串
        json_data = json.dumps(data)
        
        # 获取加密密钥
        key = Encryption.get_key(hardware_id)
        
        # 使用Fernet对称加密
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json_data.encode())
        
        return encrypted_data
    
    @staticmethod
    def decrypt_data(encrypted_data: bytes, hardware_id: str) -> Optional[Dict[str, Any]]:
        """解密数据"""
        try:
            # 获取解密密钥
            key = Encryption.get_key(hardware_id)
            
            # 使用Fernet对称解密
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data).decode()
            
            # 解析JSON
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"解密失败：{e}")
            return None


class VerificationManager:
    """管理验证信息的加载、保存和验证"""
    
    def __init__(self):
        self.hardware_id = HardwareInfo.generate_hardware_id()
        self.verification_data = None
    
    def load_verification_data(self) -> Optional[Dict[str, Any]]:
        """加载验证信息，优先尝试加密文件，然后是旧版明文文件"""
        # 尝试加载并解密二进制验证文件
        if os.path.exists(VERIFICATION_FILE):
            try:
                with open(VERIFICATION_FILE, 'rb') as f:
                    encrypted_data = f.read()
                
                data = Encryption.decrypt_data(encrypted_data, self.hardware_id)
                if data:
                    print("成功加载加密的验证信息")
                    return data
                else:
                    print("无法解密验证信息，设备可能已更换")
            except Exception as e:
                print(f"加载验证文件失败: {e}")
        
        # 如果加密文件加载失败，尝试加载旧版明文文件
        if os.path.exists(LEGACY_VERIFICATION_FILE):
            try:
                with open(LEGACY_VERIFICATION_FILE, 'r') as f:
                    data = json.load(f)
                print("成功加载旧版明文验证信息")
                return data
            except Exception as e:
                print(f"加载旧版验证文件失败: {e}")
        
        return None
    
    def save_verification_data(self, data: Dict[str, Any]) -> bool:
        """加密并保存验证信息"""
        try:
            # 添加硬件信息和时间戳
            data['hardware_id'] = self.hardware_id
            data['device_bound'] = True
            data['verified_at'] = datetime.datetime.now().isoformat()
            
            # 加密数据
            encrypted_data = Encryption.encrypt_data(data, self.hardware_id)
            
            # 保存到文件
            with open(VERIFICATION_FILE, 'wb') as f:
                f.write(encrypted_data)
            
            print("验证信息已加密保存")
            return True
        except Exception as e:
            print(f"保存验证信息失败: {e}")
            # 如果加密保存失败，尝试使用旧方式保存
            try:
                with open(LEGACY_VERIFICATION_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                print("验证信息已以旧格式保存")
                return True
            except:
                return False
    
    def is_verified(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """检查是否已经验证，并且验证信息是否与当前硬件匹配"""
        data = self.load_verification_data()
        if not data:
            return False, None
        
        # 检查硬件ID是否匹配
        if 'hardware_id' in data and data['hardware_id'] != self.hardware_id:
            print("警告：验证信息与当前设备不匹配")
            return False, data
        
        return True, data


def verify_card_key(key: str, user_identifier: str = '') -> Dict[str, Any]:
    """
    验证卡密是否有效
    
    参数:
        key (str): 要验证的卡密
        user_identifier (str, 可选): 用户标识符，用于记录谁使用了卡密
        
    返回:
        dict: 包含验证结果的字典
    """
    try:
        # 发送POST请求到API
        response = requests.post(
            API_URL,
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


def print_result(result: Dict[str, Any], verification_manager: VerificationManager) -> None:
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
        
        # 显示设备绑定状态
        is_verified, data = verification_manager.is_verified()
        if is_verified:
            print("设备状态: 已绑定到当前设备")
        else:
            print("设备状态: 新绑定")
    else:
        print("❌ 卡密验证失败!")
        print(f"原因: {result['message']}")
    print("===================\n")


def main():
    """主函数"""
    print("==== 高级卡密验证工具 ====")
    print("此工具用于验证卡密是否有效，并支持硬件绑定和验证文件加密")
    
    # 初始化验证管理器
    verification_manager = VerificationManager()
    
    # 检查是否已经验证过
    is_verified, verification_data = verification_manager.is_verified()
    if is_verified:
        print("\n您的卡密已经通过验证，无需重复验证")
        print("验证信息:")
        if verification_data.get('data'):
            print(f"卡密: {verification_data['data'].get('key', '未知')}")
            print(f"类型: {verification_data['data'].get('cardType', '未知')}")
            print(f"有效期: {verification_data['data'].get('validDays', '未知')}天")
            
            expiry_time = verification_data['data'].get('expiryTime')
            if expiry_time:
                print(f"过期时间: {expiry_time[:10]}")
            
            print("设备状态: 已绑定到当前设备")
        
        if input("\n是否重新验证? (y/n): ").lower() != 'y':
            return
    
    # 获取用户输入
    key = input("请输入卡密: ").strip()
    if not key:
        print("错误: 卡密不能为空")
        return
    
    user_id = input("请输入用户标识(可选): ").strip()
    
    print("\n正在验证卡密，请稍候...")
    result = verify_card_key(key, user_id)
    
    # 显示验证结果
    print_result(result, verification_manager)
    
    # 如果验证成功，保存验证信息
    if result['success']:
        if verification_manager.save_verification_data(result):
            print("验证信息已成功保存到本设备")
    
    # 询问用户是否继续
    while input("是否继续验证其他卡密? (y/n): ").lower() == 'y':
        key = input("请输入卡密: ").strip()
        if not key:
            print("错误: 卡密不能为空")
            continue
        
        user_id = input("请输入用户标识(可选): ").strip()
        
        print("\n正在验证卡密，请稍候...")
        result = verify_card_key(key, user_id)
        print_result(result, verification_manager)
        
        if result['success']:
            if verification_manager.save_verification_data(result):
                print("验证信息已成功保存到本设备")


def debug_hardware_info():
    """打印硬件信息，用于调试"""
    print("==== 硬件信息 ====")
    print(f"CPU ID: {HardwareInfo.get_cpu_id()}")
    print(f"硬盘序列号: {HardwareInfo.get_disk_serial()}")
    print(f"主板序列号: {HardwareInfo.get_motherboard_serial()}")
    print(f"硬件唯一标识: {HardwareInfo.generate_hardware_id()}")
    print("==================")


if __name__ == "__main__":
    try:
        # 检查是否是调试模式
        if len(sys.argv) > 1 and sys.argv[1] == "--debug":
            debug_hardware_info()
        else:
            main()
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断")
    except Exception as e:
        print(f"\n程序出错: {str(e)}")
        # 如果是调试模式，显示完整错误信息
        if len(sys.argv) > 1 and sys.argv[1] == "--debug":
            import traceback
            traceback.print_exc()
    finally:
        print("\n感谢使用高级卡密验证工具!") 