const express = require('express');
const router = express.Router();
const { getSettings, updateSettings } = require('../controllers/settingController');
const { protect, admin } = require('../middlewares/auth');

// 公开/受保护路由（根据是否登录返回不同内容）
router.get('/', getSettings);

// 仅管理员可更新设置
router.put('/', protect, admin, updateSettings);

module.exports = router; 