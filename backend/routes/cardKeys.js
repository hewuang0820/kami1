const express = require('express');
const router = express.Router();
const { 
  getCardKeys, 
  generateCardKeys, 
  deleteCardKey, 
  verifyCardKey, 
  getStatistics,
  getVerificationLogs 
} = require('../controllers/cardKeyController');
const { protect, admin } = require('../middlewares/auth');

// 公开路由
router.post('/verify', verifyCardKey);

// 受保护路由
router.get('/', protect, getCardKeys);
router.post('/generate', protect, admin, generateCardKeys);
router.delete('/:id', protect, admin, deleteCardKey);
router.get('/statistics', protect, getStatistics);
router.get('/verification-logs', protect, admin, getVerificationLogs);

module.exports = router; 