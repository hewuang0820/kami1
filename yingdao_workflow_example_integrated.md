# 影刀RPA集成卡密验证系统 - 完整流程示例（智能验证版）

本文档提供一个完整的影刀RPA流程示例，展示如何使用集成的卡密验证系统，支持智能验证（自动检查本地验证状态）。

## 文件准备

将以下文件放在影刀项目文件夹中：
- `yingdao_kami_integration.py` - 集成的卡密验证系统

## 影刀流程设计

### 方法一：智能验证流程（推荐）

#### 1. 流程开始

#### 2. Python代码组件 - 初始化系统
```python
# 导入模块
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 导入卡密验证模块
from yingdao_kami_integration import (
    初始化, 检查本地验证, 自动登录, 单码, 
    检查登录状态, 获取登录信息, 智能验证
)

# 初始化卡密验证系统
if not 初始化():
    print("卡密验证系统初始化失败")
    SetVar("init_failed", True)
else:
    print("卡密验证系统初始化成功")
    SetVar("init_failed", False)
```

#### 3. 条件判断 - 检查初始化结果
- 条件：`GetVar("init_failed") == True`
- 如果为真：跳转到"初始化失败处理"
- 如果为假：继续执行

#### 4. Python代码组件 - 检查本地验证状态
```python
# 检查本地验证状态
local_verification = 检查本地验证()

print(f"本地验证检查结果: {local_verification}")

if local_verification['valid']:
    # 本地验证有效
    SetVar("has_local_verification", True)
    SetVar("local_key", local_verification['key'])
    SetVar("local_card_type", local_verification['cardType'])
    SetVar("local_days_left", local_verification['daysLeft'])
    SetVar("local_expiry", local_verification['expiryTime'][:10] if local_verification['expiryTime'] else '')
    
    print(f"发现有效本地验证: {local_verification['key']}")
    print(f"卡密类型: {local_verification['cardType']}")
    print(f"剩余天数: {local_verification['daysLeft']}天")
    
    # 检查是否即将过期（少于7天）
    if local_verification['daysLeft'] <= 7:
        SetVar("expiry_warning", True)
        SetVar("warning_message", f"您的卡密将在 {local_verification['daysLeft']} 天后过期，请及时续费")
    else:
        SetVar("expiry_warning", False)
else:
    # 本地验证无效
    SetVar("has_local_verification", False)
    print("未找到有效的本地验证，需要输入卡密")
```

#### 5. 条件判断 - 检查本地验证状态
- 条件：`GetVar("has_local_verification") == True`
- 如果为真：跳转到"使用本地验证登录"
- 如果为假：跳转到"卡密输入流程"

#### 6. Python代码组件 - 使用本地验证登录
```python
# 使用本地验证自动登录
print("使用本地验证自动登录...")
result = 自动登录()

if "成功" in result:
    SetVar("login_success", True)
    SetVar("login_result", result)
    print(f"自动登录成功: {result}")
else:
    SetVar("login_success", False)
    SetVar("login_result", result)
    print(f"自动登录失败: {result}")
    # 本地验证失效，需要重新输入卡密
    SetVar("need_manual_input", True)
```

#### 7. 条件判断 - 检查自动登录结果
- 条件：`GetVar("login_success") == True`
- 如果为真：跳转到"检查过期提醒"
- 如果为假：跳转到"卡密输入流程"

#### 8. 条件判断 - 检查过期提醒
- 条件：`GetVar("expiry_warning") == True`
- 如果为真：显示过期提醒消息框
- 如果为假：跳转到"执行业务流程"

#### 9. 消息框 - 过期提醒
- 标题：`过期提醒`
- 内容：`{{GetVar("warning_message")}}`
- 按钮：`确定`
- 执行后：跳转到"执行业务流程"

#### 10. 输入框组件 - 卡密输入流程
- 标题：`卡密验证`
- 提示：`请输入您的卡密以继续使用软件`
- 变量名：`user_card_key`

#### 11. Python代码组件 - 验证输入的卡密
```python
# 获取用户输入的卡密
card_key = GetVar("user_card_key")

if not card_key or not card_key.strip():
    SetVar("manual_login_result", "卡密不能为空")
    SetVar("manual_login_success", False)
else:
    # 验证卡密
    print(f"正在验证卡密: {card_key.strip()}")
    result = 单码(card_key.strip())
    SetVar("manual_login_result", result)
    
    # 检查登录状态
    if 检查登录状态():
        SetVar("manual_login_success", True)
        print(f"卡密验证成功: {result}")
    else:
        SetVar("manual_login_success", False)
        print(f"卡密验证失败: {result}")
```

#### 12. 条件判断 - 检查手动验证结果
- 条件：`GetVar("manual_login_success") == True`
- 如果为真：跳转到"执行业务流程"
- 如果为假：显示验证失败消息

#### 13. 消息框 - 验证失败
- 标题：`验证失败`
- 内容：`{{GetVar("manual_login_result")}}`
- 按钮：`确定`
- 执行后：跳转到"流程结束（验证失败）"

#### 14. 执行业务流程
```python
print("=== 开始执行业务流程 ===")

# 获取当前登录信息
login_info = 获取登录信息()
print(f"当前登录状态: {login_info}")

# 显示成功消息
from xbot import app
app.message_box("验证成功", f"卡密验证通过！\n{login_info}\n\n即将开始执行业务流程...")

# 您的业务逻辑代码
# 示例：模拟业务流程
import time

for i in range(1, 4):
    print(f"执行业务步骤 {i}/3...")
    
    # 检查登录状态是否仍然有效（可选）
    if not 检查登录状态():
        print("检测到登录状态失效，停止执行")
        app.message_box("警告", "卡密状态异常，流程已停止")
        break
    
    # 模拟业务处理
    time.sleep(1)
    print(f"业务步骤 {i} 完成")

print("=== 业务流程执行完成 ===")
```

#### 15. Python代码组件 - 安全退出
```python
# 安全退出
print("正在安全退出...")
from yingdao_kami_integration import 退出
退出()
print("已安全退出卡密验证系统")
```

#### 16. 流程结束（正常结束）

### 方法二：高级智能验证流程（带重试机制）

#### 1. 流程开始

#### 2. Python代码组件 - 系统初始化
```python
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 导入所有需要的函数
from yingdao_kami_integration import (
    初始化, 检查本地验证, 自动登录, 智能验证,
    检查登录状态, 获取登录信息, 退出
)

# 初始化系统
init_success = 初始化()
SetVar("init_success", init_success)
SetVar("retry_count", 0)
SetVar("max_retries", 3)
SetVar("login_success", False)

if init_success:
    print("卡密验证系统初始化成功")
else:
    print("卡密验证系统初始化失败")
```

#### 3. 条件判断 - 检查初始化
- 条件：`GetVar("init_success") == False`
- 如果为真：跳转到"初始化失败处理"
- 如果为假：继续执行

#### 4. Python代码组件 - 智能验证尝试
```python
# 先尝试智能验证（不需要输入卡密）
print("尝试智能验证...")
result = 智能验证()

if "成功" in result:
    SetVar("login_success", True)
    SetVar("login_result", result)
    SetVar("need_manual_input", False)
    print(f"智能验证成功: {result}")
else:
    SetVar("login_success", False)
    SetVar("login_result", result)
    SetVar("need_manual_input", True)
    print(f"智能验证失败，需要手动输入卡密: {result}")
```

#### 5. 条件判断 - 检查智能验证结果
- 条件：`GetVar("login_success") == True`
- 如果为真：跳转到"执行业务流程"
- 如果为假：继续执行重试循环

#### 6. 循环开始 - 手动验证重试循环
- 循环条件：`GetVar("retry_count") < GetVar("max_retries") and GetVar("login_success") == False`

#### 7. 输入框组件 - 获取卡密
- 标题：`卡密验证`
- 提示：`智能验证失败，请手动输入卡密（剩余尝试次数：{{GetVar("max_retries") - GetVar("retry_count")}}）`
- 变量名：`user_card_key`

#### 8. Python代码组件 - 手动验证卡密
```python
# 获取用户输入
card_key = GetVar("user_card_key")
retry_count = GetVar("retry_count")

if not card_key or not card_key.strip():
    SetVar("login_result", "卡密不能为空，请重新输入")
    SetVar("login_success", False)
else:
    print(f"正在验证卡密... (第{retry_count + 1}次尝试)")
    
    # 使用智能验证函数，传入卡密
    result = 智能验证(card_key.strip())
    SetVar("login_result", result)
    
    # 检查登录状态
    if 检查登录状态():
        SetVar("login_success", True)
        login_info = 获取登录信息()
        SetVar("login_info", login_info)
        print(f"登录成功: {login_info}")
        
        # 成功后跳出循环
        SetVar("retry_count", GetVar("max_retries"))
    else:
        SetVar("login_success", False)
        # 增加重试次数
        SetVar("retry_count", retry_count + 1)
        
        if retry_count + 1 >= GetVar("max_retries"):
            print("验证失败次数过多，程序将退出")
        else:
            print(f"验证失败，还有 {GetVar('max_retries') - retry_count - 1} 次机会")
```

#### 9. 消息框 - 显示当前验证结果
- 标题：`验证结果`
- 内容：`{{GetVar("login_result")}}`
- 按钮：`确定`

#### 10. 循环结束

#### 11. 条件判断 - 最终检查登录状态
- 条件：`GetVar("login_success") == True`
- 如果为真：跳转到"执行业务流程"
- 如果为假：跳转到"验证失败处理"

#### 12-16. [执行业务流程、安全退出等步骤与方法一相同]

## 新增功能说明

### 1. 智能验证
- **自动检查**：每次启动时自动检查本地验证状态
- **无感登录**：如果本地验证有效，用户无需输入卡密
- **过期提醒**：卡密即将过期时（少于7天）会显示提醒

### 2. 本地验证状态检查
```python
# 检查本地验证状态
local_check = 检查本地验证()
print(f"验证状态: {local_check}")

# 返回格式:
# {
#     'valid': True/False,           # 是否有效
#     'key': '卡密',                 # 卡密内容
#     'cardType': '卡密类型',         # 卡密类型
#     'expiryTime': '过期时间',       # 过期时间
#     'daysLeft': 剩余天数,           # 剩余天数
#     'message': '错误消息'           # 错误消息（如果有）
# }
```

### 3. 智能验证函数
```python
# 智能验证：优先使用本地验证，失败时才使用卡密
result = 智能验证()  # 仅检查本地验证
result = 智能验证("XXXX-XXXX-XXXX-XXXX")  # 提供卡密作为备选
```

## 流程图总览（智能验证版）

```
[开始] → [初始化] → [初始化成功?]
                        ↓ No
                   [初始化失败处理] → [结束]
                        ↓ Yes
                   [检查本地验证] → [本地验证有效?]
                                      ↓ Yes
                                 [自动登录] → [登录成功?]
                                              ↓ Yes
                                         [检查过期提醒] → [执行业务流程] → [结束]
                                              ↓ No
                                         [手动输入卡密] → [验证卡密] → [成功?]
                                                                    ↓ Yes
                                                               [执行业务流程] → [结束]
                                                                    ↓ No
                                                               [重试或失败] → [结束]
                        ↓ No
                   [手动输入卡密] → [验证卡密] → [重试循环]
```

## 使用优势

1. **用户体验优化**：首次验证后，后续使用无需重复输入卡密
2. **离线支持**：验证成功后可在有效期内离线使用
3. **智能提醒**：即将过期时自动提醒用户续费
4. **安全保障**：硬件绑定确保卡密不被盗用
5. **容错机制**：本地验证失效时自动降级到手动验证

## 注意事项

1. **首次使用**：首次验证卡密时需要联网
2. **硬件绑定**：卡密与设备硬件信息绑定，更换设备需重新验证
3. **过期处理**：卡密过期后需要重新输入有效卡密
4. **文件保护**：验证文件采用硬件绑定加密，确保安全性

这个智能验证版本大大提升了用户体验，避免了每次使用都要输入卡密的麻烦，同时保持了高度的安全性。 