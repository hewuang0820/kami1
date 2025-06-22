# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

import threading
import time
import json
import hashlib
import winreg
import wmi
import os
import signal
import win32api
import win32con
import ctypes.wintypes
import binascii
import inspect
import requests
import platform
import uuid
import subprocess
import base64
import datetime
from enum import IntEnum
from typing import List, Dict, Any, Optional, Tuple, Union

# 安装必要的库
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import algorithms
except ImportError:
    os.system('pip install cryptography requests')
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import algorithms

# 配置常量
DEFAULT_API_URL = 'http://170.106.175.187/api/card-keys/verify'
DEFAULT_VERIFICATION_FILE = 'verification.bin'
DEFAULT_SALT = b'kami_verification_system_salt'

class Result:
    """API调用结果类"""
    code: int = -998
    msg: str = ""
    data: str = ""

class KamiHeartbeatFailure:
    """心跳失败结果类"""
    错误编码: int = 0
    错误消息: str = ""

class LocalVerificationResult:
    """本地验证结果类"""
    有效: bool = False
    卡密: str = ""
    卡密类型: str = ""
    到期时间: str = ""
    剩余天数: int = 0
    错误消息: str = ""

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

class KamiLoginResult:
    """卡密登录结果类"""
    错误编码: int = -999
    错误消息: str = "服务器访问失败，您本地网络不顺畅，请检查下"
    服务器时间戳: int = 0
    到期时间: str = ""
    剩余点数: int = 0
    角色ID: str = ""
    角色名称: str = ""
    备注: str = ""
    卡密类型: str = ""

class KamiInitResult:
    """初始化结果类"""
    错误编码: int = -999
    错误消息: str = "初始化失败"
    服务器时间戳: int = 0

class Singleton(object):
    """单例模式基类"""
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        cls._lock.acquire()
        if not hasattr(cls, '_inst'):
            try:
                cls._inst = super(Singleton, cls).__new__(cls)
            except:
                cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
        cls._lock.release()
        return cls._inst

class KamiSDK(Singleton):
    """卡密验证SDK主类"""
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.__hardware_id = HardwareInfo.generate_hardware_id()
        self.__api_url = DEFAULT_API_URL
        self.__verification_file = DEFAULT_VERIFICATION_FILE
        self.__encryption = KamiEncryption()
        
        # 登录状态
        self.__is_login = False
        self.__current_login_key = ""
        self.__login_data = None
        self.__heartbeat_thread = None
        self.__is_stop_heartbeat = False
        self.__heartbeat_callback = None
        
        # 线程锁
        self.__login_lock = threading.Lock()
        self.__heartbeat_lock = threading.Lock()
        
        print(f"卡密SDK初始化完成，硬件ID: {self.__hardware_id[:8]}...")
    
    def __verify_card_key_api(self, key: str, user_identifier: str = '') -> Dict[str, Any]:
        """调用API验证卡密"""
        try:
            response = requests.post(
                self.__api_url,
                json={'key': key, 'userIdentifier': user_identifier},
                timeout=10
            )
            
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
    
    def __save_verification_data(self, data: Dict[str, Any]) -> bool:
        """保存验证数据到本地"""
        try:
            # 添加硬件ID和保存时间
            save_data = {
                'hardware_id': self.__hardware_id,
                'save_time': datetime.datetime.now().isoformat(),
                'data': data.get('data', {}),
                'success': data.get('success', False),
                'message': data.get('message', ''),
                'verified_key': data.get('data', {}).get('key', '')  # 保存验证过的卡密
            }
            
            encrypted_data = self.__encryption.encrypt_data(save_data)
            
            with open(self.__verification_file, 'wb') as f:
                f.write(encrypted_data)
            
            print(f"验证数据已保存，卡密: {save_data['verified_key']}")
            return True
        except Exception as e:
            print(f"保存验证数据失败: {e}")
            return False
    
    def __load_verification_data(self) -> Optional[Dict[str, Any]]:
        """加载本地验证数据"""
        try:
            if os.path.exists(self.__verification_file):
                with open(self.__verification_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.__encryption.decrypt_data(encrypted_data)
                if decrypted_data:
                    # 检查硬件ID是否匹配
                    if decrypted_data.get('hardware_id') == self.__hardware_id:
                        # 检查是否过期
                        expiry_time = decrypted_data.get('data', {}).get('expiryTime')
                        if expiry_time:
                            try:
                                # 尝试多种日期格式解析
                                expiry = None
                                
                                # 格式1: ISO格式 (2023-12-31T23:59:59)
                                try:
                                    expiry = datetime.datetime.fromisoformat(expiry_time)
                                except ValueError:
                                    pass
                                
                                # 格式2: 带Z的UTC格式 (2023-12-31T23:59:59Z)
                                if expiry is None:
                                    try:
                                        if expiry_time.endswith('Z'):
                                            expiry_time_clean = expiry_time[:-1]
                                            expiry = datetime.datetime.fromisoformat(expiry_time_clean)
                                        else:
                                            expiry = datetime.datetime.fromisoformat(expiry_time)
                                    except ValueError:
                                        pass
                                
                                # 格式3: 标准格式 (2023-12-31 23:59:59)
                                if expiry is None:
                                    try:
                                        expiry = datetime.datetime.strptime(expiry_time, '%Y-%m-%d %H:%M:%S')
                                    except ValueError:
                                        pass
                                
                                # 格式4: 日期格式 (2023-12-31)
                                if expiry is None:
                                    try:
                                        expiry = datetime.datetime.strptime(expiry_time[:10], '%Y-%m-%d')
                                    except ValueError:
                                        pass
                                
                                # 如果所有格式都失败，记录错误但不阻止程序运行
                                if expiry is None:
                                    print(f"警告: 无法解析过期时间格式: {expiry_time}")
                                    # 假设已过期，要求重新验证
                                    return None
                                
                                # 检查是否过期
                                if datetime.datetime.now() < expiry:
                                    verified_key = decrypted_data.get('verified_key', '')
                                    print(f"本地验证有效，过期时间: {expiry}, 验证过的卡密: {verified_key}")
                                    return decrypted_data
                                else:
                                    print(f"本地验证已过期: {expiry}")
                                    return None
                                    
                            except Exception as date_error:
                                print(f"日期解析错误: {date_error}")
                                return None
                        else:
                            print("警告: 验证数据中没有过期时间信息")
                            return None
                    else:
                        print("硬件ID不匹配，本地验证无效")
                        return None
                else:
                    print("无法解密验证数据")
                    return None
            else:
                print("验证文件不存在")
                return None
                
        except Exception as e:
            print(f"加载验证数据失败: {e}")
            # 如果是文件损坏，尝试删除损坏的文件
            try:
                if os.path.exists(self.__verification_file):
                    os.remove(self.__verification_file)
                    print("已删除损坏的验证文件")
            except:
                pass
            return None
    
    def __is_verified(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """检查是否已验证"""
        data = self.__load_verification_data()
        if data and data.get('success', False):
            return True, data
        return False, None
    
    def __heartbeat_worker(self):
        """心跳检测工作线程"""
        self.__heartbeat_lock.acquire()
        
        try:
            while not self.__is_stop_heartbeat and self.__is_login:
                # 检查本地验证是否仍然有效
                is_valid, data = self.__is_verified()
                
                if not is_valid:
                    # 本地验证失效，触发心跳失败回调
                    if self.__heartbeat_callback:
                        failure = KamiHeartbeatFailure()
                        failure.错误编码 = 6003  # 卡密到期
                        failure.错误消息 = "卡密已过期或无效"
                        
                        try:
                            self.__heartbeat_callback(failure)
                        except Exception as e:
                            print(f"心跳回调执行失败: {e}")
                    
                    break
                
                print("心跳检测正常...")
                
                # 等待5分钟
                for _ in range(300):  # 5分钟 = 300秒
                    if self.__is_stop_heartbeat:
                        break
                    time.sleep(1)
        
        except Exception as e:
            print(f"心跳检测异常: {e}")
        
        finally:
            print("心跳检测已停止")
            self.__heartbeat_lock.release()
    
    def 初始化软件函数(self, heartbeat_callback=None) -> KamiInitResult:
        """初始化软件"""
        result = KamiInitResult()
        
        try:
            self.__heartbeat_callback = heartbeat_callback
            result.错误编码 = 0
            result.错误消息 = "初始化成功"
            result.服务器时间戳 = int(time.time())
            
            print("卡密验证系统初始化成功")
            
        except Exception as e:
            result.错误编码 = -1
            result.错误消息 = f"初始化失败: {str(e)}"
        
        return result
    
    def 单码登录函数(self, card_key: str, user_identifier: str = '') -> KamiLoginResult:
        """卡密登录"""
        self.__login_lock.acquire()
        
        result = KamiLoginResult()
        
        try:
            if self.__is_login:
                result.错误编码 = -7
                result.错误消息 = "请先退出当前登录"
                return result
            
            if not card_key or not card_key.strip():
                result.错误编码 = -5
                result.错误消息 = "卡密不能为空"
                return result
            
            card_key = card_key.strip()
            
            # 首先检查本地是否已有有效验证
            is_valid, local_data = self.__is_verified()
            if is_valid and local_data:
                verified_key = local_data.get('verified_key', '')
                
                # 检查是否是同一个卡密或者本地验证仍然有效
                if verified_key == card_key or verified_key == '':
                    # 使用本地数据登录
                    self.__is_login = True
                    self.__current_login_key = card_key
                    self.__login_data = local_data.get('data', {})
                    
                    result.错误编码 = 0
                    result.错误消息 = "登录成功（使用本地验证）"
                    result.到期时间 = self.__login_data.get('expiryTime', '')
                    result.卡密类型 = self.__login_data.get('cardType', '')
                    result.剩余点数 = self.__login_data.get('validDays', 0)
                    
                    # 如果本地验证的卡密为空，更新为当前卡密
                    if verified_key == '':
                        local_data['verified_key'] = card_key
                        local_data['data']['key'] = card_key
                        self.__save_verification_data({
                            'success': True,
                            'data': local_data['data']
                        })
                        print(f"更新本地验证卡密: {card_key}")
                    
                    # 启动心跳检测
                    self.__start_heartbeat()
                    
                    print(f"使用本地验证登录成功: {card_key}")
                    return result
                else:
                    print(f"卡密不匹配，本地验证卡密: {verified_key}, 输入卡密: {card_key}")
            
            # 在线验证卡密
            print("正在验证卡密...")
            api_result = self.__verify_card_key_api(card_key, user_identifier)
            
            if api_result.get('success', False):
                # 验证成功，保存到本地
                # 确保保存的数据包含卡密信息
                if 'data' in api_result and api_result['data']:
                    api_result['data']['key'] = card_key
                
                self.__save_verification_data(api_result)
                
                self.__is_login = True
                self.__current_login_key = card_key
                self.__login_data = api_result.get('data', {})
                
                result.错误编码 = 0
                result.错误消息 = "登录成功"
                result.到期时间 = self.__login_data.get('expiryTime', '')
                result.卡密类型 = self.__login_data.get('cardType', '')
                result.剩余点数 = self.__login_data.get('validDays', 0)
                
                # 启动心跳检测
                self.__start_heartbeat()
                
                print(f"卡密登录成功: {card_key}")
                
            else:
                result.错误编码 = 1001
                result.错误消息 = api_result.get('message', '卡密验证失败')
                print(f"卡密验证失败: {result.错误消息}")
        
        except Exception as e:
            result.错误编码 = -1
            result.错误消息 = f"登录过程出错: {str(e)}"
            print(f"登录异常: {e}")
        
        finally:
            self.__login_lock.release()
        
        return result
    
    def __start_heartbeat(self):
        """启动心跳检测"""
        if self.__heartbeat_thread and self.__heartbeat_thread.is_alive():
            return
        
        self.__is_stop_heartbeat = False
        self.__heartbeat_thread = threading.Thread(target=self.__heartbeat_worker)
        self.__heartbeat_thread.daemon = True
        self.__heartbeat_thread.start()
        
        print("心跳检测已启动")
    
    def 退出登录函数(self) -> Result:
        """退出登录"""
        result = Result()
        
        try:
            if not self.__is_login:
                result.code = 0
                result.msg = "未登录状态"
                return result
            
            # 停止心跳检测
            self.__is_stop_heartbeat = True
            if self.__heartbeat_thread and self.__heartbeat_thread.is_alive():
                print("等待心跳线程结束...")
                self.__heartbeat_thread.join(timeout=5)
            
            # 清理登录状态
            self.__is_login = False
            self.__current_login_key = ""
            self.__login_data = None
            
            result.code = 0
            result.msg = "退出登录成功"
            
            print("已退出登录")
        
        except Exception as e:
            result.code = -1
            result.msg = f"退出登录失败: {str(e)}"
        
        return result
    
    def 检查登录状态(self) -> bool:
        """检查是否已登录"""
        return self.__is_login
    
    def 获取登录信息(self) -> Optional[Dict[str, Any]]:
        """获取当前登录信息"""
        if self.__is_login and self.__login_data:
            return {
                'key': self.__current_login_key,
                'cardType': self.__login_data.get('cardType', ''),
                'expiryTime': self.__login_data.get('expiryTime', ''),
                'validDays': self.__login_data.get('validDays', 0)
            }
        return None
    
    def 关闭当前软件(self):
        """强制关闭软件"""
        try:
            print("正在关闭软件...")
            self.退出登录函数()
            os.kill(os.getpid(), signal.SIGTERM)
        except:
            try:
                os._exit(1)
            except:
                pass

    def 检查本地验证状态(self) -> LocalVerificationResult:
        """检查本地验证状态，返回详细信息"""
        result = LocalVerificationResult()
        
        try:
            is_valid, data = self.__is_verified()
            
            if is_valid and data:
                card_data = data.get('data', {})
                result.有效 = True
                result.卡密 = card_data.get('key', '')
                result.卡密类型 = card_data.get('cardType', '')
                result.到期时间 = card_data.get('expiryTime', '')
                result.剩余点数 = card_data.get('validDays', 0)
                
                # 计算实际剩余天数
                if result.到期时间:
                    try:
                        # 使用相同的日期解析逻辑
                        expiry = None
                        expiry_time = result.到期时间
                        
                        # 尝试多种格式
                        try:
                            expiry = datetime.datetime.fromisoformat(expiry_time)
                        except ValueError:
                            try:
                                if expiry_time.endswith('Z'):
                                    expiry_time = expiry_time[:-1]
                                expiry = datetime.datetime.fromisoformat(expiry_time)
                            except ValueError:
                                try:
                                    expiry = datetime.datetime.strptime(expiry_time, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    try:
                                        expiry = datetime.datetime.strptime(expiry_time[:10], '%Y-%m-%d')
                                    except ValueError:
                                        pass
                        
                        if expiry:
                            now = datetime.datetime.now()
                            days_left = (expiry - now).days
                            result.剩余天数 = max(0, days_left)
                        
                    except Exception as e:
                        print(f"计算剩余天数时出错: {e}")
                        result.剩余天数 = 0
                
                print(f"发现有效的本地验证: {result.卡密}, 类型: {result.卡密类型}, 剩余: {result.剩余天数}天")
            else:
                result.有效 = False
                result.错误消息 = "未找到有效的本地验证或验证已过期"
                print("未找到有效的本地验证")
                
        except Exception as e:
            result.有效 = False
            result.错误消息 = f"检查本地验证时出错: {str(e)}"
            print(f"检查本地验证异常: {e}")
        
        return result
    
    def 使用本地验证登录(self) -> KamiLoginResult:
        """使用本地验证数据直接登录"""
        result = KamiLoginResult()
        
        try:
            if self.__is_login:
                result.错误编码 = -7
                result.错误消息 = "已经登录，请先退出"
                return result
            
            is_valid, local_data = self.__is_verified()
            
            if is_valid and local_data:
                card_data = local_data.get('data', {})
                
                # 设置登录状态
                self.__is_login = True
                self.__current_login_key = card_data.get('key', '')
                self.__login_data = card_data
                
                result.错误编码 = 0
                result.错误消息 = "使用本地验证登录成功"
                result.到期时间 = card_data.get('expiryTime', '')
                result.卡密类型 = card_data.get('cardType', '')
                result.剩余点数 = card_data.get('validDays', 0)
                
                # 启动心跳检测
                self.__start_heartbeat()
                
                print(f"使用本地验证登录成功: {self.__current_login_key}")
                
            else:
                result.错误编码 = 1002
                result.错误消息 = "本地验证无效或已过期"
                
        except Exception as e:
            result.错误编码 = -1
            result.错误消息 = f"本地验证登录失败: {str(e)}"
            print(f"本地验证登录异常: {e}")
        
        return result

# 全局SDK实例
kami_sdk = KamiSDK()

# 心跳失败回调函数
def 接收心跳失败的函数(failure: KamiHeartbeatFailure):
    """心跳失败处理函数"""
    print(f"心跳失败 - 错误编码：{failure.错误编码}")
    print(f"心跳失败 - 错误消息：{failure.错误消息}")
    
    # 根据错误编码处理不同情况
    if failure.错误编码 == 6003:  # 卡密到期
        print("卡密已到期，请续费")
    elif failure.错误编码 == 6005:  # 卡密被禁用
        print("卡密已被禁用")
    elif failure.错误编码 == 6004:  # 卡密点数不足
        print("卡密点数不足")
    
    # 强制关闭软件
    kami_sdk.关闭当前软件()

# 初始化函数
def 初始化():
    """初始化卡密验证系统"""
    result = kami_sdk.初始化软件函数(接收心跳失败的函数)
    if result.错误编码 == 0:
        print("卡密验证系统初始化成功")
        return True
    else:
        print(f"初始化失败: {result.错误消息}")
        return False

# 检查本地验证状态
def 检查本地验证() -> dict:
    """检查本地是否有有效验证，返回验证状态信息"""
    result = kami_sdk.检查本地验证状态()
    
    return {
        'valid': result.有效,
        'key': result.卡密,
        'cardType': result.卡密类型,
        'expiryTime': result.到期时间,
        'daysLeft': result.剩余天数,
        'message': result.错误消息
    }

# 使用本地验证自动登录
def 自动登录() -> str:
    """使用本地验证自动登录"""
    result = kami_sdk.使用本地验证登录()
    
    if result.错误编码 == 0:
        return f"自动登录成功，类型：{result.卡密类型}，到期时间：{result.到期时间[:10]}，有效天数：{result.剩余点数}天"
    else:
        return f"自动登录失败：{result.错误消息}"

# 卡密登录函数
def 单码(卡密: str, 用户标识: str = '') -> str:
    """卡密登录"""
    result = kami_sdk.单码登录函数(卡密, 用户标识)
    
    if result.错误编码 == 0:
        return f"卡密登录成功，类型：{result.卡密类型}，到期时间：{result.到期时间[:10]}，有效天数：{result.剩余点数}天"
    else:
        return f"卡密登录失败：{result.错误消息}"

# 智能验证函数（推荐使用）
def 智能验证(卡密: str = '', 用户标识: str = '') -> str:
    """智能验证：先检查本地验证，无效时才使用卡密验证"""
    # 先检查本地验证
    local_check = 检查本地验证()
    
    if local_check['valid']:
        # 本地验证有效，直接使用
        auto_result = 自动登录()
        if "成功" in auto_result:
            return f"使用本地验证登录成功，{auto_result}"
    
    # 本地验证无效，需要卡密验证
    if not 卡密 or not 卡密.strip():
        return "本地验证无效，需要提供卡密进行验证"
    
    # 使用卡密验证
    return 单码(卡密.strip(), 用户标识)

# 检查登录状态
def 检查登录状态() -> bool:
    """检查是否已登录"""
    return kami_sdk.检查登录状态()

# 获取登录信息
def 获取登录信息() -> str:
    """获取当前登录信息"""
    info = kami_sdk.获取登录信息()
    if info:
        return f"当前登录卡密：{info['key']}，类型：{info['cardType']}，到期时间：{info['expiryTime'][:10]}"
    else:
        return "未登录"

# 退出登录
def 退出():
    """退出登录"""
    result = kami_sdk.退出登录函数()
    if result.code == 0:
        print("退出登录成功")
    else:
        print(f"退出登录失败：{result.msg}")

# 调试函数
def 调试验证文件() -> str:
    """调试验证文件，返回详细信息"""
    try:
        verification_file = DEFAULT_VERIFICATION_FILE
        
        if not os.path.exists(verification_file):
            return "验证文件不存在"
        
        # 检查文件大小
        file_size = os.path.getsize(verification_file)
        result = f"验证文件存在，大小: {file_size} 字节\n"
        
        # 尝试读取文件
        try:
            with open(verification_file, 'rb') as f:
                encrypted_data = f.read()
            result += f"成功读取加密数据，长度: {len(encrypted_data)}\n"
        except Exception as e:
            return result + f"读取文件失败: {e}"
        
        # 尝试解密
        try:
            encryption = KamiEncryption()
            decrypted_data = encryption.decrypt_data(encrypted_data)
            if decrypted_data:
                result += "解密成功\n"
                result += f"数据结构: {list(decrypted_data.keys())}\n"
                
                # 检查硬件ID
                hardware_id = HardwareInfo.generate_hardware_id()
                stored_hardware_id = decrypted_data.get('hardware_id', '')
                result += f"当前硬件ID: {hardware_id[:16]}...\n"
                result += f"存储硬件ID: {stored_hardware_id[:16]}...\n"
                result += f"硬件ID匹配: {hardware_id == stored_hardware_id}\n"
                
                # 检查验证过的卡密
                verified_key = decrypted_data.get('verified_key', '')
                result += f"验证过的卡密: {verified_key}\n"
                
                # 检查数据内容
                data = decrypted_data.get('data', {})
                result += f"卡密数据: {data}\n"
                
                # 检查过期时间
                expiry_time = data.get('expiryTime', '')
                if expiry_time:
                    result += f"原始过期时间: {expiry_time}\n"
                    
                    # 尝试解析日期
                    try:
                        if expiry_time.endswith('Z'):
                            expiry_time_clean = expiry_time[:-1]
                            expiry = datetime.datetime.fromisoformat(expiry_time_clean)
                        else:
                            expiry = datetime.datetime.fromisoformat(expiry_time)
                        
                        now = datetime.datetime.now()
                        days_left = (expiry - now).days
                        result += f"解析后过期时间: {expiry}\n"
                        result += f"当前时间: {now}\n"
                        result += f"剩余天数: {days_left}\n"
                        result += f"是否有效: {days_left > 0}\n"
                        
                    except Exception as date_error:
                        result += f"日期解析失败: {date_error}\n"
                else:
                    result += "没有过期时间信息\n"
                    
            else:
                result += "解密失败\n"
                
        except Exception as e:
            result += f"解密过程出错: {e}\n"
        
        return result
        
    except Exception as e:
        return f"调试过程出错: {e}"

# 清理验证文件函数
def 清理验证文件() -> str:
    """清理损坏的验证文件"""
    try:
        verification_file = DEFAULT_VERIFICATION_FILE
        if os.path.exists(verification_file):
            os.remove(verification_file)
            return "验证文件已删除，下次使用时需要重新验证卡密"
        else:
            return "验证文件不存在"
    except Exception as e:
        return f"删除验证文件失败: {e}"

# 主函数（用于测试）
def main():
    """主函数"""
    print("=== 卡密验证系统测试 ===")
    
    # 初始化
    if not 初始化():
        return
    
    # 调试验证文件
    print("\n=== 调试信息 ===")
    debug_info = 调试验证文件()
    print(debug_info)
    
    # 检查本地验证
    local_check = 检查本地验证()
    print(f"\n本地验证状态: {local_check}")
    
    if local_check['valid']:
        # 使用本地验证登录
        result = 自动登录()
        print(result)
    else:
        # 需要卡密验证
        test_key = input("请输入测试卡密: ").strip()
        if test_key:
            result = 单码(test_key)
            print(result)
    
    if 检查登录状态():
        print(获取登录信息())
        
        # 等待用户输入后退出
        input("按回车键退出...")
        退出()

if __name__ == "__main__":
    main() 