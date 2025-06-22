# 影刀RPA卡密验证流程示例

本文档提供一个完整的影刀RPA流程示例，展示如何在影刀中实现卡密验证功能，确保只有拥有有效卡密的用户才能执行特定流程。

## 流程概述

这个示例流程实现了以下功能：
1. 检查设备是否已有有效卡密
2. 如果没有有效卡密，要求用户输入卡密
3. 验证卡密是否有效
4. 根据验证结果决定是否继续执行业务流程

## 准备工作

1. 将以下文件放在影刀项目文件夹中：
   - `verification_utils.py`（卡密验证核心库）
   - `kami_integration_for_yingdao.py`（影刀集成工具）

2. 确保已安装必要的Python库：
   ```
   pip install requests cryptography
   ```

## 流程设计

### 1. 流程开始节点

首先创建一个新的影刀流程，添加流程开始节点。

### 2. 检查是否已有有效卡密

添加一个Python代码组件，用于检查设备是否已有有效卡密：

```python
# 检查是否已有有效卡密
import sys
import os
import traceback

try:
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # 导入验证工具
    from kami_integration_for_yingdao import KamiVerificationForYingdao
    
    # 创建验证器并检查
    verifier = KamiVerificationForYingdao()
    has_valid_key = verifier.check_verification()
    
    # 设置变量
    SetVar("has_valid_key", has_valid_key)
    
    print(f"设备卡密验证状态: {'已验证' if has_valid_key else '未验证'}")
except Exception as e:
    print(f"检查卡密状态时出错: {str(e)}")
    print(traceback.format_exc())
    SetVar("has_valid_key", False)
```

### 3. 条件判断节点

添加一个条件判断节点，检查`has_valid_key`变量：
- 条件表达式：`GetVar("has_valid_key") == True`
- 如果条件为真：跳转到"执行业务流程"节点
- 如果条件为假：继续执行下一步

### 4. 显示卡密输入框

添加一个输入框组件，用于收集用户输入的卡密：
- 标题：`卡密验证`
- 提示信息：`请输入卡密以继续执行流程`
- 变量名：`kami_key`

### 5. 验证卡密

添加一个Python代码组件，用于验证用户输入的卡密：

```python
# 验证用户输入的卡密
import sys
import os
import json
import traceback

try:
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # 导入验证函数
    from kami_integration_for_yingdao import verify_kami_for_yingdao
    
    # 获取用户输入的卡密
    kami_key = GetVar("kami_key")
    
    # 验证卡密
    verification_result = verify_kami_for_yingdao(kami_key)
    
    # 解析JSON结果
    result = json.loads(verification_result)
    
    # 设置验证结果变量
    SetVar("verification_success", result["success"])
    SetVar("verification_message", result.get("message", ""))
    
    if result["success"]:
        print("卡密验证成功!")
    else:
        print(f"卡密验证失败: {result.get('message', '未知错误')}")
except Exception as e:
    print(f"验证卡密时出错: {str(e)}")
    print(traceback.format_exc())
    SetVar("verification_success", False)
    SetVar("verification_message", f"验证过程出错: {str(e)}")
```

### 6. 验证结果处理

添加一个条件判断节点，检查`verification_success`变量：
- 条件表达式：`GetVar("verification_success") == True`
- 如果条件为真：跳转到"执行业务流程"节点
- 如果条件为假：继续执行下一步

### 7. 显示验证失败消息

添加一个消息框组件，显示验证失败的消息：
- 标题：`验证失败`
- 消息内容：`卡密验证失败: {{GetVar("verification_message")}}`
- 按钮：`确定`

### 8. 结束流程（验证失败）

添加一个流程结束节点，标记为"验证失败结束"。

### 9. 执行业务流程

添加一个注释节点，标记为"开始执行业务流程"。

在这里添加您的实际业务流程逻辑。例如，可以添加一个消息框显示：
- 标题：`验证成功`
- 消息内容：`卡密验证成功，正在执行业务流程...`
- 按钮：`确定`

### 10. 结束流程（正常结束）

添加一个流程结束节点，标记为"正常结束"。

## 完整流程图

```
[流程开始] → [检查是否已有有效卡密] → [条件判断:has_valid_key]
     ↓ (False)                           ↓ (True)
[显示卡密输入框] → [验证卡密] → [条件判断:verification_success] → [执行业务流程] → [正常结束]
                                  ↓ (False)
                           [显示验证失败消息] → [验证失败结束]
```

## 高级功能扩展

### 1. 添加重试功能

在验证失败后，可以添加重试功能：

```python
# 在验证失败消息框后添加
SetVar("retry_count", GetVar("retry_count", 0) + 1)

# 添加条件判断
if GetVar("retry_count") < 3:
    # 跳转回卡密输入框
    JumpTo("显示卡密输入框")
else:
    # 超过重试次数，结束流程
    MessageBox("错误", "验证失败次数过多，流程已终止")
    EndFlow()
```

### 2. 添加卡密有效期检查

在业务流程执行前，检查卡密是否即将过期：

```python
# 检查卡密有效期
import sys
import os
import json
import datetime

try:
    # 导入验证工具
    from kami_integration_for_yingdao import KamiVerificationForYingdao
    
    # 创建验证器并获取验证信息
    verifier = KamiVerificationForYingdao()
    is_valid, data = verifier.verifier.is_verified()
    
    if is_valid and 'data' in data:
        # 获取过期时间
        expiry_time = data['data'].get('expiryTime')
        if expiry_time:
            # 解析过期时间
            expiry = datetime.datetime.fromisoformat(expiry_time)
            now = datetime.datetime.now()
            days_left = (expiry - now).days
            
            # 设置剩余天数变量
            SetVar("days_left", days_left)
            
            # 如果剩余天数少于7天，显示提醒
            if days_left <= 7:
                MessageBox("提醒", f"您的卡密将在 {days_left} 天后过期，请及时续费")
except Exception as e:
    print(f"检查卡密有效期时出错: {str(e)}")
```

## 注意事项

1. **错误处理**：示例中包含了基本的错误处理，确保即使在出错情况下也能正常运行
2. **变量命名**：确保变量名不与影刀中的其他变量冲突
3. **路径处理**：示例使用了相对路径，如果文件不在同一目录，需要调整路径
4. **Python环境**：确保影刀能够访问到正确的Python环境

## 故障排除

如果流程执行出现问题，可以尝试以下方法：

1. **检查Python环境**：确保Python环境正确安装了所需库
2. **检查文件路径**：确保验证相关文件在正确的位置
3. **启用调试输出**：在Python代码中添加更多的`print`语句，帮助定位问题
4. **检查网络连接**：首次验证需要联网，确保能够正常访问API服务器

## 结论

通过这个示例流程，您可以在影刀RPA中集成卡密验证功能，确保只有拥有有效卡密的用户才能执行特定流程。这种方式可以有效保护您的RPA流程，防止未授权使用。 