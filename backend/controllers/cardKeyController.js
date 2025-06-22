const CardKey = require('../models/CardKey');

// 生成随机卡密
const generateRandomKey = (format = 'XXXX-XXXX-XXXX-XXXX') => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let key = '';
  
  if (format === 'XXXXXXXXXXXXXXXX') {
    // 无分隔符格式
    for (let i = 0; i < 16; i++) {
      key += chars.charAt(Math.floor(Math.random() * chars.length));
    }
  } else if (format === 'XXXX-XXXX-XXXX') {
    // 3组格式
    for (let j = 0; j < 3; j++) {
      for (let k = 0; k < 4; k++) {
        key += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      if (j < 2) key += '-';
    }
  } else {
    // 默认4组格式
    for (let j = 0; j < 4; j++) {
      for (let k = 0; k < 4; k++) {
        key += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      if (j < 3) key += '-';
    }
  }
  
  return key;
};

// @desc    获取所有卡密
// @route   GET /api/card-keys
// @access  私有
exports.getCardKeys = async (req, res) => {
  try {
    // 获取查询参数
    const { status, search, page = 1, limit = 10 } = req.query;
    
    // 构建查询条件
    const query = {};
    if (status) {
      query.status = status;
    }
    if (search) {
      query.key = { $regex: search, $options: 'i' };
    }
    
    // 执行查询
    const cardKeys = await CardKey.find(query)
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit));
    
    // 获取总数
    const total = await CardKey.countDocuments(query);
    
    res.status(200).json({
      success: true,
      count: cardKeys.length,
      total,
      page: parseInt(page),
      pages: Math.ceil(total / limit),
      data: cardKeys
    });
  } catch (error) {
    console.error('Get card keys error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    生成新卡密
// @route   POST /api/card-keys/generate
// @access  私有
exports.generateCardKeys = async (req, res) => {
  try {
    const { count = 5, validDays = 30, format = 'XXXX-XXXX-XXXX-XXXX', cardType = '时长卡' } = req.body;
    
    // 限制生成数量
    if (count < 1 || count > 100) {
      return res.status(400).json({
        success: false,
        message: '生成数量必须在1到100之间'
      });
    }
    
    // 检查卡密类型
    if (!['时长卡'].includes(cardType)) {
      return res.status(400).json({
        success: false,
        message: '卡密类型必须是"时长卡"'
      });
    }
    
    // 生成卡密
    const newCardKeys = [];
    for (let i = 0; i < count; i++) {
      let isUnique = false;
      let newKey;
      
      // 确保卡密唯一
      while (!isUnique) {
        newKey = generateRandomKey(format);
        // 检查是否已存在
        const exists = await CardKey.findOne({ key: newKey });
        if (!exists) {
          isUnique = true;
        }
      }
      
      // 创建新卡密
      const cardKey = await CardKey.create({
        key: newKey,
        validDays,
        status: '未使用',
        cardType
      });
      
      newCardKeys.push(cardKey);
    }
    
    res.status(201).json({
      success: true,
      message: `成功生成${count}个卡密`,
      data: newCardKeys
    });
  } catch (error) {
    console.error('Generate card keys error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    删除卡密
// @route   DELETE /api/card-keys/:id
// @access  私有
exports.deleteCardKey = async (req, res) => {
  try {
    // 使用findByIdAndDelete直接查找并删除文档
    const cardKey = await CardKey.findByIdAndDelete(req.params.id);
    
    if (!cardKey) {
      return res.status(404).json({
        success: false,
        message: '未找到该卡密'
      });
    }
    
    res.status(200).json({
      success: true,
      message: '卡密已删除'
    });
  } catch (error) {
    console.error('Delete card key error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    验证卡密
// @route   POST /api/card-keys/verify
// @access  公开
exports.verifyCardKey = async (req, res) => {
  try {
    const { key, userIdentifier } = req.body;
    
    if (!key) {
      return res.status(400).json({
        success: false,
        message: '请提供卡密'
      });
    }
    
    // 获取用户IP
    const userIP = req.headers['x-forwarded-for'] || 
                   req.connection.remoteAddress || 
                   req.socket.remoteAddress ||
                   (req.connection.socket ? req.connection.socket.remoteAddress : null);
    
    // 查找卡密
    const cardKey = await CardKey.findOne({ key });
    
    if (!cardKey) {
      return res.status(404).json({
        success: false,
        message: '卡密不存在'
      });
    }
    
    // 检查卡密状态
    if (cardKey.status === '已使用') {
      // 检查是否过期
      if (cardKey.isExpired()) {
        cardKey.status = '已过期';
        await cardKey.save();
        return res.status(400).json({
          success: false,
          message: '卡密已过期'
        });
      } else {
        return res.status(400).json({
          success: false,
          message: '卡密已被使用'
        });
      }
    }
    
    if (cardKey.status === '已过期') {
      return res.status(400).json({
        success: false,
        message: '卡密已过期'
      });
    }
    
    // 使用卡密
    await cardKey.useKey(userIdentifier, userIP);
    
    res.status(200).json({
      success: true,
      message: '卡密验证成功',
      data: {
        key: cardKey.key,
        validDays: cardKey.validDays,
        useTime: cardKey.useTime,
        expiryTime: cardKey.expiryTime,
        cardType: cardKey.cardType
      }
    });
  } catch (error) {
    console.error('Verify card key error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    获取卡密统计信息
// @route   GET /api/card-keys/statistics
// @access  私有
exports.getStatistics = async (req, res) => {
  try {
    const total = await CardKey.countDocuments();
    const used = await CardKey.countDocuments({ status: '已使用' });
    const unused = await CardKey.countDocuments({ status: '未使用' });
    const expired = await CardKey.countDocuments({ status: '已过期' });
    
    res.status(200).json({
      success: true,
      data: {
        total,
        used,
        unused,
        expired
      }
    });
  } catch (error) {
    console.error('Get statistics error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    获取卡密验证记录
// @route   GET /api/card-keys/verification-logs
// @access  私有
exports.getVerificationLogs = async (req, res) => {
  try {
    // 获取查询参数
    const { page = 1, limit = 10 } = req.query;
    
    // 构建查询条件 - 只查询已使用的卡密
    const query = { 
      status: { $in: ['已使用', '已过期'] },
      useTime: { $ne: null }
    };
    
    // 执行查询 - 使用lean()方法获取普通JavaScript对象而不是Mongoose文档
    const verificationLogs = await CardKey.find(query)
      .select('key useTime userIP verificationStatus')
      .sort({ useTime: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))
      .lean(); // 添加lean()方法以获取普通JavaScript对象
    
    // 获取总数
    const total = await CardKey.countDocuments(query);
    
    res.status(200).json({
      success: true,
      count: verificationLogs.length,
      total,
      page: parseInt(page),
      pages: Math.ceil(total / limit),
      data: verificationLogs.map(log => ({
        id: log._id,
        key: log.key,
        useTime: log.useTime,
        userIP: log.userIP || 'Unknown',
        status: log.verificationStatus || '验证成功'
      }))
    });
  } catch (error) {
    console.error('Get verification logs error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
}; 