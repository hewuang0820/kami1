const Setting = require('../models/Setting');

// @desc    获取系统设置
// @route   GET /api/settings
// @access  公开(部分)/私有(完整)
exports.getSettings = async (req, res) => {
  try {
    // 查找设置，如果不存在则创建默认设置
    let settings = await Setting.findOne();
    
    if (!settings) {
      settings = await Setting.create({});
    }
    
    // 如果是公开访问，只返回部分设置
    if (!req.user) {
      return res.status(200).json({
        success: true,
        data: {
          systemName: settings.systemName,
          keyFormat: settings.keyFormat,
          maintenanceMode: settings.maintenanceMode
        }
      });
    }
    
    // 管理员返回所有设置
    res.status(200).json({
      success: true,
      data: settings
    });
  } catch (error) {
    console.error('Get settings error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
};

// @desc    更新系统设置
// @route   PUT /api/settings
// @access  私有
exports.updateSettings = async (req, res) => {
  try {
    const { systemName, adminEmail, keyFormat, allowRegistration, maintenanceMode } = req.body;
    
    // 查找设置，如果不存在则创建默认设置
    let settings = await Setting.findOne();
    
    if (!settings) {
      settings = await Setting.create({});
    }
    
    // 更新设置
    if (systemName !== undefined) settings.systemName = systemName;
    if (adminEmail !== undefined) settings.adminEmail = adminEmail;
    if (keyFormat !== undefined) settings.keyFormat = keyFormat;
    if (allowRegistration !== undefined) settings.allowRegistration = allowRegistration;
    if (maintenanceMode !== undefined) settings.maintenanceMode = maintenanceMode;
    
    await settings.save();
    
    res.status(200).json({
      success: true,
      message: '系统设置已更新',
      data: settings
    });
  } catch (error) {
    console.error('Update settings error:', error);
    res.status(500).json({
      success: false,
      message: '服务器错误'
    });
  }
}; 