const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');

// 配置环境变量
dotenv.config();

// 初始化Express应用
const app = express();

// 中间件
// 配置CORS，允许所有来源的请求
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());

// 连接MongoDB
mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/kami-system')
  .then(() => console.log('MongoDB连接成功'))
  .catch(err => console.error('MongoDB连接失败', err));

// 导入路由
const authRoutes = require('./routes/auth');
const cardKeyRoutes = require('./routes/cardKeys');
const settingsRoutes = require('./routes/settings');

// 使用路由
app.use('/api/auth', authRoutes);
app.use('/api/card-keys', cardKeyRoutes);
app.use('/api/settings', settingsRoutes);

// 定义端口
const PORT = process.env.PORT || 5000;

// 启动服务器
app.listen(PORT, () => {
  console.log(`服务器运行在端口 ${PORT}`);
}); 