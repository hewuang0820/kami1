# 卡密验证系统阿里云部署指南

本文档提供了将卡密验证系统部署到阿里云ECS服务器的详细步骤。

## 1. 准备工作

### 阿里云ECS服务器
- 确保您的阿里云ECS实例已开通并运行
- 推荐配置：至少1核2G内存，CentOS/Ubuntu系统
- 确保已开放以下端口：
  - 22端口(SSH)
  - 80端口(HTTP)
  - 443端口(HTTPS，如需配置SSL)
  - 5000端口(或您计划用于API的其他端口)

### 本地准备
- 在Windows系统上安装Git，用于代码管理
- 安装远程连接工具(如PuTTY、XShell或Windows Terminal)
- 安装文件传输工具(如WinSCP或FileZilla)

## 2. 服务器环境配置

### 连接到服务器
使用SSH客户端连接到您的阿里云ECS实例：
```bash
ssh root@your_server_ip
```

### 安装Node.js
```bash
# 更新包管理器
apt update -y  # Ubuntu系统
# 或
yum update -y  # CentOS系统

# 安装Node.js 18.x
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -  # CentOS
# 或
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -  # Ubuntu

# 安装Node.js和npm
yum install -y nodejs  # CentOS
# 或
apt-get install -y nodejs  # Ubuntu

# 验证安装
node -v
npm -v
```

### 安装MongoDB
您有两个选择：在ECS实例上安装MongoDB或使用阿里云MongoDB云数据库服务。

#### 选项1：在ECS上安装MongoDB
```bash
# CentOS系统
cat > /etc/yum.repos.d/mongodb-org-6.0.repo <<EOF
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF

yum install -y mongodb-org
systemctl start mongod
systemctl enable mongod

# Ubuntu系统
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
apt-get update
apt-get install -y mongodb-org
systemctl start mongod
systemctl enable mongod

# 验证MongoDB安装
mongosh --eval 'db.runCommand({ connectionStatus: 1 })'
```

#### 选项2：使用阿里云MongoDB云数据库
1. 在阿里云控制台创建MongoDB实例
2. 设置安全组规则，允许ECS实例连接到MongoDB实例
3. 记录连接字符串，稍后会在环境变量中使用

### 安装Nginx(用于提供前端静态文件和API反向代理)
```bash
# CentOS系统
yum install -y nginx

# Ubuntu系统
apt-get install -y nginx

# 启动Nginx并设置开机自启
systemctl start nginx
systemctl enable nginx
```

## 3. 部署后端

### 创建应用目录
```bash
mkdir -p /var/www/kami-system
cd /var/www/kami-system
```

### 上传后端代码
使用WinSCP或FileZilla将本地backend目录中的文件上传到服务器的`/var/www/kami-system/backend`目录。

或者，如果您的代码在Git仓库中：
```bash
git clone your_repository_url /var/www/kami-system
```

### 配置环境变量
创建`.env`文件设置必要的环境变量：
```bash
cd /var/www/kami-system/backend
cat > .env <<EOF
PORT=5000
# 如果使用本地MongoDB
MONGO_URI=mongodb://localhost:27017/kami-system
# 如果使用阿里云MongoDB云数据库
# MONGO_URI=mongodb://username:password@your_mongodb_instance_address:port/kami-system?authSource=admin
# JWT密钥，请更改为强密码
JWT_SECRET=your_very_strong_secret_key
# JWT过期时间
JWT_EXPIRES_IN=7d
EOF
```

### 安装依赖并启动服务
```bash
cd /var/www/kami-system/backend
npm install
# 测试运行
node server.js
```

如果服务器正常启动，按Ctrl+C停止测试运行，然后安装PM2来管理Node.js应用：
```bash
npm install -g pm2
pm2 start server.js --name "kami-system-api"
pm2 save
pm2 startup
```

## 4. 部署前端

### 修改前端配置
编辑前端的`config.js`文件，将API基础URL更改为您的服务器地址：

```bash
cd /var/www/kami-system
cat > config.js <<EOF
/**
 * 前端配置文件
 */

// API基础URL
const API_BASE_URL = 'http://your_server_ip:5000/api';
// 如果使用Nginx反向代理，可以设置为
// const API_BASE_URL = '/api';

// API端点
const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: `\${API_BASE_URL}/auth/login`,
    INIT: `\${API_BASE_URL}/auth/init`,
    ME: `\${API_BASE_URL}/auth/me`,
    CHANGE_PASSWORD: `\${API_BASE_URL}/auth/change-password`,
  },
  
  // 卡密相关
  CARD_KEYS: {
    BASE: `\${API_BASE_URL}/card-keys`,
    GENERATE: `\${API_BASE_URL}/card-keys/generate`,
    VERIFY: `\${API_BASE_URL}/card-keys/verify`,
    STATISTICS: `\${API_BASE_URL}/card-keys/statistics`,
  },
  
  // 系统设置
  SETTINGS: {
    BASE: `\${API_BASE_URL}/settings`,
  }
};

// 导出配置
const config = {
  API_BASE_URL,
  API_ENDPOINTS,
  TOKEN_KEY: 'kami_system_token',
  DEFAULT_AVATAR: 'https://via.placeholder.com/100',
  PAGE_SIZE: 10,
};

// 在全局范围内暴露配置
window.APP_CONFIG = config; 
EOF
```

### 上传前端文件
使用WinSCP或FileZilla将前端文件(index.html、app.js、style.css等)上传到服务器的`/var/www/kami-system`目录。

### 配置Nginx
创建Nginx配置文件：
```bash
cat > /etc/nginx/conf.d/kami-system.conf <<EOF
server {
    listen 80;
    server_name your_server_ip_or_domain;
    root /var/www/kami-system;
    index index.html;

    # 前端静态文件
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API反向代理
    location /api {
        proxy_pass http://localhost:5000/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# 测试Nginx配置
nginx -t

# 如果配置正确，重启Nginx
systemctl restart nginx
```

## 5. 系统测试与维护

### 测试部署
在浏览器中访问`http://your_server_ip`或您配置的域名，测试卡密验证系统是否正常工作。

### 日志查看
- 查看Nginx日志：
  ```bash
  tail -f /var/log/nginx/access.log
  tail -f /var/log/nginx/error.log
  ```
- 查看PM2日志：
  ```bash
  pm2 logs kami-system-api
  ```

### 系统维护
- 更新后端代码：
  ```bash
  cd /var/www/kami-system/backend
  # 上传新代码后
  npm install  # 如有新依赖
  pm2 restart kami-system-api
  ```
- 更新前端代码：
  ```bash
  # 只需上传新的前端文件到/var/www/kami-system目录
  ```

## 6. 安全建议

1. **启用防火墙**：只开放必要端口
   ```bash
   # CentOS
   yum install -y firewalld
   systemctl start firewalld
   systemctl enable firewalld
   firewall-cmd --permanent --add-service=ssh
   firewall-cmd --permanent --add-service=http
   firewall-cmd --permanent --add-service=https
   firewall-cmd --permanent --add-port=5000/tcp
   firewall-cmd --reload
   
   # Ubuntu
   apt-get install -y ufw
   ufw allow ssh
   ufw allow http
   ufw allow https
   ufw allow 5000/tcp
   ufw enable
   ```

2. **设置SSL证书**：使用Let's Encrypt为您的域名配置HTTPS
   ```bash
   # 安装Certbot
   apt-get install -y certbot python3-certbot-nginx  # Ubuntu
   # 或
   yum install -y certbot python3-certbot-nginx  # CentOS
   
   # 获取并安装证书
   certbot --nginx -d your_domain.com
   ```

3. **定期更新系统和依赖**：
   ```bash
   # 更新系统
   apt update && apt upgrade -y  # Ubuntu
   # 或
   yum update -y  # CentOS
   
   # 更新Node.js依赖
   cd /var/www/kami-system/backend
   npm update
   ```

4. **定期备份数据**：
   ```bash
   # MongoDB备份
   mongodump --out /var/backups/mongodb/$(date +"%Y-%m-%d")
   
   # 自动化备份脚本
   cat > /etc/cron.daily/mongodb-backup <<EOF
   #!/bin/bash
   BACKUP_DIR="/var/backups/mongodb/\$(date +"%Y-%m-%d")"
   mkdir -p \$BACKUP_DIR
   mongodump --out \$BACKUP_DIR
   
   # 保留最近30天的备份
   find /var/backups/mongodb/ -type d -mtime +30 -exec rm -rf {} \;
   EOF
   chmod +x /etc/cron.daily/mongodb-backup
   ```

## 7. 故障排除

### 后端服务无法启动
- 检查MongoDB连接：`systemctl status mongod`
- 检查端口占用：`netstat -tulpn | grep 5000`
- 检查日志：`pm2 logs kami-system-api`

### 前端无法访问API
- 检查Nginx配置：`nginx -t`
- 验证API服务是否运行：`curl http://localhost:5000/api/settings`
- 检查防火墙规则：`firewall-cmd --list-all`或`ufw status`

### 数据库连接问题
- 检查MongoDB服务状态：`systemctl status mongod`
- 验证连接字符串格式
- 检查数据库用户权限 