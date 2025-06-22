const jwt = require('jsonwebtoken');
const User = require('../models/User');

// 保护路由中间件 - 验证token
exports.protect = async (req, res, next) => {
  let token;
  
  // 从请求头中获取token
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }
  
  // 检查token是否存在
  if (!token) {
    return res.status(401).json({
      success: false,
      message: '未授权，请登录'
    });
  }
  
  try {
    // 验证token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'kami_system_secret_key');
    
    // 获取用户信息
    const user = await User.findById(decoded.id).select('-password');
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: '无效的用户Token'
      });
    }
    
    // 将用户信息添加到请求对象
    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: '未授权，请登录'
    });
  }
};

// 验证管理员权限
exports.admin = (req, res, next) => {
  if (req.user && req.user.role === 'admin') {
    next();
  } else {
    return res.status(403).json({
      success: false,
      message: '需要管理员权限'
    });
  }
}; 