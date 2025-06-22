# 卡密验证系统 - 高级功能

本项目提供了卡密验证系统的扩展功能，包括硬件绑定和验证文件加密功能，防止卡密被复制到其他设备使用。

## 主要功能

- **硬件绑定**: 将卡密与特定设备的硬件信息绑定
- **验证文件加密**: 加密存储验证信息，防止直接复制验证文件
- **多平台支持**: 支持Windows、Linux和macOS
- **多种验证模式**: 支持一次性验证和周期性验证
- **功能级别控制**: 根据卡密类型提供不同级别的功能

## 文件说明

- **verify_card_key_advanced.py**: 完整的高级卡密验证工具，包含命令行界面
- **verification_utils.py**: 核心功能库，可以集成到其他项目中
- **kami_integration_examples.py**: 各种集成示例，展示如何在不同场景下使用卡密验证

## 安装依赖

```bash
pip install requests cryptography
```

## 使用方法

### 1. 直接使用验证工具

```bash
# 运行高级卡密验证工具
python verify_card_key_advanced.py

# 查看硬件信息(调试模式)
python verify_card_key_advanced.py --debug
```

### 2. 集成到自己的项目

```python
# 导入验证工具库
from verification_utils import verify_card, is_card_valid, KamiVerifier

# 方法1: 使用便捷函数验证卡密
result = verify_card('XXXX-XXXX-XXXX-XXXX', 'user123')
if result['success']:
    print('卡密验证成功')
else:
    print('卡密验证失败:', result['message'])

# 方法2: 检查是否已有有效卡密
if is_card_valid():
    print('设备已有有效卡密')
else:
    print('需要验证卡密')

# 方法3: 使用KamiVerifier类进行更多自定义操作
verifier = KamiVerifier(
    api_url='http://170.106.175.187/api/card-keys/verify',  # 可自定义API地址
    verification_file='my_verification.bin',  # 可自定义验证文件路径
    legacy_file='my_verification.json'  # 可自定义旧版文件路径
)

# 检查是否已验证
is_valid, data = verifier.is_verified()
if is_valid:
    print('设备已验证，卡密信息:', data['data'])
```

### 3. 查看集成示例

运行集成示例，了解不同场景下的应用:

```bash
python kami_integration_examples.py
```

集成示例包括:
- 应用程序启动保护
- 软件功能解锁
- 周期性校验
- 配置文件绑定
- 自定义验证参数

## 硬件绑定机制

硬件绑定通过收集以下设备信息生成唯一标识符:

- CPU ID
- 硬盘序列号
- 主板序列号

这些信息被组合并通过SHA-256算法生成一个唯一的硬件ID，验证文件与此ID绑定，确保在其他设备上无法使用。

## 验证文件加密

验证信息使用Fernet对称加密算法进行加密，密钥基于设备的硬件ID生成，确保即使验证文件被复制到其他设备，也无法解密使用。

## API调用

API端点: `http://170.106.175.187/api/card-keys/verify`

请求格式:
```json
{
  "key": "XXXX-XXXX-XXXX-XXXX",
  "userIdentifier": "用户标识(可选)"
}
```

响应格式:
```json
{
  "success": true,
  "data": {
    "key": "XXXX-XXXX-XXXX-XXXX",
    "cardType": "标准版",
    "validDays": 30,
    "expiryTime": "2023-12-31T23:59:59"
  }
}
```

## 兼容性

- 支持旧版明文验证文件向新版加密文件的平滑升级
- 支持在无法获取特定硬件信息时使用备选方案
- 在Windows/Linux/macOS上均可运行，但获取硬件信息的方法可能有所不同

## 注意事项

1. 首次使用需要联网验证卡密
2. 需要安装requests和cryptography库
3. 在某些系统上获取硬件信息可能需要管理员/root权限
4. 验证文件默认保存在当前目录下

## 更多信息

有关API的更多信息，请参考卡密验证系统的完整文档。 