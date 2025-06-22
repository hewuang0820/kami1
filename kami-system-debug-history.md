# 卡密验证系统 问题排查与修复经验记录

## 一、常见问题与排查思路

### 1. 路由404/401/500错误
- 404：路由未注册或路径拼写错误
- 401：权限校验失败，未带token或token过期
- 500：后端代码异常，常见于参数为undefined或数据库操作异常

### 2. Nginx代理问题
- 检查Nginx配置是否有`location /api`代理到Node.js
- 用curl分别测试`localhost:5000`和`127.0.0.1/api`，定位是Nginx还是Node.js问题

### 3. 前端API请求异常
- 检查config.js的API_BASE_URL配置
- F12抓包，确认请求路径、状态码、请求头（token）

### 4. 数据字段名不一致
- 前端传递id字段，后端实际为`_id`，导致删除等操作失败
- 解决：前端统一用`card._id`作为主键

---

## 二、典型修复案例

### 1. 验证记录接口404
- 现象：前端/后端curl都404
- 原因：Node.js路由未注册或服务未重启
- 解决：检查server.js和routes/cardKeys.js，确认路由注册，重启服务

### 2. 删除卡密500错误
- 现象：F12抓包发现DELETE请求id为undefined
- 原因：前端传递了`card.id`，实际应为`card._id`
- 解决：index.html中将`deleteCard(card.id)`改为`deleteCard(card._id)`

### 3. 权限校验导致401
- 现象：curl不带token返回401
- 解决：前端自动带token，curl测试时手动加Authorization头

### 4. Nginx未代理/api
- 现象：所有/api请求404
- 解决：在Nginx配置中添加`location /api { proxy_pass http://localhost:5000; ... }`

---

## 三、排查流程建议

1. 先curl本地端口，确认Node.js服务路由是否生效
2. 再curl 127.0.0.1/api，确认Nginx代理是否生效
3. F12抓包，确认前端请求路径、token、响应
4. 检查前后端字段名、参数传递是否一致
5. 每次改动后，务必重启Node.js服务

---

## 四、经验总结

- 路由、权限、代理、字段名，是全栈项目最常见的坑
- curl和F12抓包是最有效的排查工具
- 只要分步定位，问题一定能解决！ 