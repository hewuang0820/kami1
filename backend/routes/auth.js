const express = require('express');
const router = express.Router();
const { login, getMe, changePassword, initAdmin } = require('../controllers/authController');
const { protect } = require('../middlewares/auth');

// 公开路由
router.post('/login', login);
router.post('/init', initAdmin);

// 受保护路由
router.get('/me', protect, getMe);
router.put('/change-password', protect, changePassword);

module.exports = router; 