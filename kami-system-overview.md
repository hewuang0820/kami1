# 卡密验证系统 项目结构与功能说明

## 一、项目结构

```
kami-verification-system/
├── backend/                  # 后端Node.js服务
│   ├── controllers/          # 业务控制器（如cardKeyController.js）
│   ├── middlewares/          # 权限等中间件
│   ├── models/               # Mongoose数据模型
│   ├── routes/               # 路由定义
│   ├── server.js             # 后端主入口
│   └── package.json          # 后端依赖
├── index.html                # 前端主页面
├── app.js                    # 前端Vue主逻辑
├── style.css                 # 前端样式
├── config.js                 # 前端API配置
├── verify_card_key.py        # Python卡密验证工具
├── verify_card_key_advanced.py # Python高级验证工具
├── verification_utils.py     # Python验证核心库
├── kami_integration_examples.py # Python集成示例
├── readme.md                 # 项目说明
└── deployment-guide.md       # 部署指南
```

## 二、主要功能

### 1. 前端功能
- 管理员登录/登出
- 卡密管理（生成、删除、导出、分页、搜索）
- 统计分析（卡密状态分布、总数、已用、未用、过期）
- 使用记录（卡密验证历史）
- 系统设置（系统名、邮箱、卡密格式、密码修改）
- API调用示例（多语言）

### 2. 后端功能
- RESTful API（卡密增删查、验证、统计、日志）
- JWT权限认证与管理员权限校验
- MongoDB数据存储
- Nginx反向代理支持

### 3. Python工具
- 支持命令行卡密验证
- 支持硬件绑定、加密验证文件
- 可集成到其他项目

### 4. 部署
- 支持Linux服务器（Nginx+Node.js+MongoDB）
- 支持前后端分离和反向代理

---

## 三、技术栈

- 前端：Vue2 + Axios + Chart.js + 原生HTML/CSS
- 后端：Node.js + Express + Mongoose + JWT
- 数据库：MongoDB
- 服务器：Nginx反向代理
- 工具：Python（requests、cryptography）

---

## 四、API端点举例

- POST `/api/auth/login`         # 管理员登录
- GET  `/api/card-keys`          # 获取卡密列表
- POST `/api/card-keys/generate` # 生成卡密
- DELETE `/api/card-keys/:id`    # 删除卡密
- GET  `/api/card-keys/statistics` # 获取统计
- GET  `/api/card-keys/verification-logs` # 获取验证记录

---

## 五、特色亮点

- 支持卡密硬件绑定与加密
- 多平台、多语言API调用示例
- 管理后台功能完善
- 支持权限分级与安全认证 