const mongoose = require('mongoose');

const CardKeySchema = new mongoose.Schema({
  key: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  status: {
    type: String,
    enum: ['未使用', '已使用', '已过期'],
    default: '未使用'
  },
  cardType: {
    type: String,
    enum: ['时长卡'],
    default: '时长卡'
  },
  validDays: {
    type: Number,
    required: true,
    min: 1
  },
  createTime: {
    type: Date,
    default: Date.now
  },
  useTime: {
    type: Date,
    default: null
  },
  expiryTime: {
    type: Date,
    default: null
  },
  usedBy: {
    type: String,
    default: null
  },
  userIP: {
    type: String,
    default: null
  },
  verificationStatus: {
    type: String,
    enum: ['验证成功', '验证失败'],
    default: null
  }
}, {
  timestamps: true
});

// 检查卡密是否过期
CardKeySchema.methods.isExpired = function() {
  if (this.status === '已使用' && this.useTime) {
    const expiryDate = new Date(this.useTime);
    expiryDate.setDate(expiryDate.getDate() + this.validDays);
    return new Date() > expiryDate;
  }
  return false;
};

// 使用卡密
CardKeySchema.methods.useKey = function(userIdentifier, userIP) {
  this.status = '已使用';
  this.useTime = new Date();
  this.usedBy = userIdentifier || null;
  this.userIP = userIP || null;
  this.verificationStatus = '验证成功';
  
  // 计算过期时间
  const expiryDate = new Date(this.useTime);
  expiryDate.setDate(expiryDate.getDate() + this.validDays);
  this.expiryTime = expiryDate;
  
  return this.save();
};

module.exports = mongoose.model('CardKey', CardKeySchema); 