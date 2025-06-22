#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
卡密验证系统工具库
提供硬件绑定和验证文件加密的核心功能，方便集成到其他项目
"""

import os
import sys
import json
import platform
import uuid
import subprocess
import base64
import hashlib
import datetime
from typing import Dict, Any, Optional, Tuple, Union

try:
    import requests  # type: ignore
    # cryptography 可能在某些环境未安装，运行时才必需；
    # 加上 "type: ignore" 以消除 Pyright 的 missing-import 警告。
    from cryptography.fernet import Fernet  # type: ignore
    from cryptography.hazmat.primitives import hashes  # type: ignore
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # type: ignore
except ImportError:
    # 在静态分析或缺少依赖时提供兜底定义，防止 IDE 报错
    import types
    requests = types.ModuleType("requests")  # type: ignore
    Fernet = hashes = PBKDF2HMAC = object  # type: ignore
    print("[警告] 未安装 requests 或 cryptography，运行前请执行:\n  pip install requests cryptography")
    sys.exit(1)

# 默认配置
DEFAULT_API_URL = 'http://170.106.175.187/api/card-keys/verify'
DEFAULT_VERIFICATION_FILE = 'verification.bin'
DEFAULT_LEGACY_FILE = 'verification.json'
DEFAULT_SALT = b'kami_verification_system_salt'


class HardwareInfo:
    """硬件信息收集工具类"""
    
    @staticmethod
    def get_cpu_id() -> str:
        """获取CPU ID"""
        if platform.system() == "Windows":
            try:
                output = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode()
                return output.strip().split('\n')[1].strip()
            except:
                pass
        elif platform.system() == "Linux":
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('serial') or line.startswith('Serial'):
                            return line.strip().split(':')[1].strip()
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                output = subprocess.check_output("ioreg -l | grep IOPlatformSerialNumber", shell=True).decode()
                return output.strip().split('=')[1].strip().replace('"', '')
            except:
                pass
        
        return platform.processor() + platform.machine()
    
    @staticmethod
    def get_disk_serial() -> str:
        """获取硬盘序列号"""
        if platform.system() == "Windows":
            try:
                output = subprocess.check_output("wmic diskdrive get SerialNumber", shell=True).decode()
                serial = output.strip().split('\n')[1].strip()
                return serial if serial and serial != "" else str(uuid.getnode())
            except:
                pass
        elif platform.system() == "Linux":
            try:
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
                output = subprocess.check_output("wmic baseboard get SerialNumber", shell=True).decode()
                return output.strip().split('\n')[1].strip()
            except:
                pass
        elif platform.system() == "Linux":
            try:
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
        
        hardware_info = f"{cpu_id}|{disk_serial}|{motherboard_serial}"
        hardware_hash = hashlib.sha256(hardware_info.encode()).hexdigest()
        
        return hardware_hash


class KamiEncryption:
    """卡密验证加密工具类"""
    
    def __init__(self, salt: bytes = DEFAULT_SALT):
        self.salt = salt
    
    def get_key_from_hardware(self) -> bytes:
        """从当前硬件生成加密密钥"""
        hardware_id = HardwareInfo.generate_hardware_id()
        return self.get_key(hardware_id)
    
    def get_key(self, hardware_id: str) -> bytes:
        """从硬件ID生成加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(hardware_id.encode()))
        return key
    
    def encrypt_data(self, data: Dict[str, Any], hardware_id: Optional[str] = None) -> bytes:
        """加密数据"""
        json_data = json.dumps(data)
        
        if hardware_id is None:
            hardware_id = HardwareInfo.generate_hardware_id()
            
        key = self.get_key(hardware_id)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json_data.encode())
        
        return encrypted_data
    
    def decrypt_data(self, encrypted_data: bytes, hardware_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """解密数据"""
        try:
            if hardware_id is None:
                hardware_id = HardwareInfo.generate_hardware_id()
                
            key = self.get_key(hardware_id)
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data).decode()
            
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"解密失败：{e}")
            return None


class KamiVerifier:
    """卡密验证工具类"""
    
    def __init__(self, 
                 api_url: str = DEFAULT_API_URL,
                 verification_file: str = DEFAULT_VERIFICATION_FILE,
                 legacy_file: str = DEFAULT_LEGACY_FILE):
        self.api_url = api_url
        self.verification_file = verification_file
        self.legacy_file = legacy_file
        self.hardware_id = HardwareInfo.generate_hardware_id()
        self.encryption = KamiEncryption()
    
    def verify_card_key(self, key: str, user_identifier: str = '') -> Dict[str, Any]:
        """验证卡密是否有效"""
        try:
            response = requests.post(
                self.api_url,
                json={'key': key, 'userIdentifier': user_identifier},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # 如果验证成功，保存验证信息
                if result.get('success', False):
                    self.save_verification_data(result)
                return result
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
    
    def load_verification_data(self) -> Optional[Dict[str, Any]]:
        """加载验证信息，优先尝试加密文件，然后是旧版明文文件"""
        # 尝试加载加密文件
        if os.path.exists(self.verification_file):
            try:
                with open(self.verification_file, 'rb') as f:
                    encrypted_data = f.read()
                
                data = self.encryption.decrypt_data(encrypted_data, self.hardware_id)
                if data:
                    return data
            except:
                pass
        
        # 尝试加载旧版明文文件
        if os.path.exists(self.legacy_file):
            try:
                with open(self.legacy_file, 'r') as f:
                    data = json.load(f)
                return data
            except:
                pass
        
        return None
    
    def save_verification_data(self, data: Dict[str, Any]) -> bool:
        """加密并保存验证信息"""
        try:
            # 添加硬件信息和时间戳
            data['hardware_id'] = self.hardware_id
            data['device_bound'] = True
            data['verified_at'] = datetime.datetime.now().isoformat()
            
            # 加密数据
            encrypted_data = self.encryption.encrypt_data(data, self.hardware_id)
            
            # 保存到文件
            with open(self.verification_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except:
            # 如果加密保存失败，尝试使用旧方式保存
            try:
                with open(self.legacy_file, 'w') as f:
                    json.dump(data, f, indent=2)
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
            return False, data
        
        # 检查是否已过期
        if 'data' in data and 'expiryTime' in data['data']:
            expiry_time = data['data']['expiryTime']
            try:
                # 格式如 2023-12-31T23:59:59
                expiry_date = datetime.datetime.fromisoformat(expiry_time)
                if expiry_date < datetime.datetime.now():
                    return False, data
            except:
                pass
        
        return True, data


# 便捷函数，可以直接导入使用
def verify_card(key: str, user_id: str = '') -> Dict[str, Any]:
    """
    验证卡密是否有效的便捷函数
    
    参数:
        key (str): 卡密
        user_id (str, 可选): 用户标识
    
    返回:
        Dict[str, Any]: 验证结果
    """
    verifier = KamiVerifier()
    return verifier.verify_card_key(key, user_id)


def is_card_valid() -> bool:
    """
    检查当前设备上的卡密是否有效
    
    返回:
        bool: 卡密是否有效
    """
    verifier = KamiVerifier()
    is_valid, _ = verifier.is_verified()
    return is_valid


def get_hardware_id() -> str:
    """
    获取当前设备的硬件ID
    
    返回:
        str: 硬件ID
    """
    return HardwareInfo.generate_hardware_id()


# 以下是示例用法
if __name__ == "__main__":
    # 演示硬件信息收集
    print("===== 硬件信息 =====")
    print(f"CPU ID: {HardwareInfo.get_cpu_id()}")
    print(f"硬盘序列号: {HardwareInfo.get_disk_serial()}")
    print(f"主板序列号: {HardwareInfo.get_motherboard_serial()}")
    print(f"硬件唯一标识: {HardwareInfo.generate_hardware_id()}")
    
    # 演示验证功能
    print("\n===== 卡密验证 =====")
    verifier = KamiVerifier()
    is_valid, data = verifier.is_verified()
    
    if is_valid:
        print("此设备已经验证过卡密")
        if data and 'data' in data:
            print(f"卡密: {data['data'].get('key', '未知')}")
            print(f"过期时间: {data['data'].get('expiryTime', '未知')}")
    else:
        print("此设备尚未验证卡密或验证已过期")
        key = input("请输入卡密进行验证: ")
        if key:
            result = verifier.verify_card_key(key)
            print("验证结果:", result['success'])
            if result['success']:
                print("卡密验证成功并已绑定到当前设备") 