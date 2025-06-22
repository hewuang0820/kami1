const jwt = require('jsonwebtoken');
const User = require('../models/User');

// 生成JWT Token
const generateToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET || 'kami_system_secret_key', {
    expiresIn: '30d'
  });
};

// @desc    用户登录
// @route   POST /api/auth/login
// @access  公开
exports.login = async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // 检查是否提供了用户名和密码
    if (!username || !password) {
      return res.status(400).json({
        success: false,
        message: '请提供用户名和密码'
      });
    }
    
    // 查找用户
    const user = await User.findOne({ username });
    
    // 检查用户是否存在并验证密码
    if (!user || !(await user.matchPassword(password))) {
      return res.status(401).json({
        success: false,
        message: '用户名或密码错误'
      });
    }
    
    // 更新最后登录时间
    user.lastLogin = Date.now();
    await user.save();
    
    // 生成并返回token
    res.status(200).json({
      success: true,
      token: generateToken(user._id),
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        role: user.role
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    获取当前登录用户信息
// @route   GET /api/auth/me
// @access  私有
exports.getMe = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    
    res.status(200).json({
      success: true,
      user
    });
  } catch (error) {
    console.error('Get me error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    修改密码
// @route   PUT /api/auth/change-password
// @access  私有
exports.changePassword = async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;
    
    // 检查是否提供了当前密码和新密码
    if (!currentPassword || !newPassword) {
      return res.status(400).json({
        success: false,
        message: '请提供当前密码和新密码'
      });
    }
    
    // 获取用户
    const user = await User.findById(req.user.id);
    
    // 验证当前密码
    if (!(await user.matchPassword(currentPassword))) {
      return res.status(401).json({
        success: false,
        message: '当前密码不正确'
      });
    }
    
    // 更新密码
    user.password = newPassword;
    await user.save();
    
    res.status(200).json({
      success: true,
      message: '密码已成功更新'
    });
  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    创建初始管理员账户
// @route   POST /api/auth/init
// @access  公开(仅首次使用)
exports.initAdmin = async (req, res) => {
  try {
    // 检查是否已有管理员账户
    const adminCount = await User.countDocuments();
    
    if (adminCount > 0) {
      return res.status(400).json({
        success: false,
        message: '管理员账户已存在，不能重复初始化'
      });
    }
    
    // 创建默认管理员
    const admin = await User.create({
      username: 'admin',
      password: 'admin123',
      email: 'admin@example.com',
      role: 'admin'
    });
    
    res.status(201).json({
      success: true,
      message: '初始管理员账户已创建',
      admin: {
        id: admin._id,
        username: admin.username,
        email: admin.email
      }
    });
  } catch (error) {
    console.error('Init admin error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
}; 