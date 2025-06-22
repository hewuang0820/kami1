const mongoose = require('mongoose');

const SettingSchema = new mongoose.Schema({
  systemName: {
    type: String,
    default: '卡密验证系统'
  },
  adminEmail: {
    type: String,
    default: 'admin@example.com'
  },
  keyFormat: {
    type: String,
    enum: ['XXXX-XXXX-XXXX-XXXX', 'XXXXXXXXXXXXXXXX', 'XXXX-XXXX-XXXX'],
    default: 'XXXX-XXXX-XXXX-XXXX'
  },
  allowRegistration: {
    type: Boolean,
    default: false
  },
  maintenanceMode: {
    type: Boolean,
    default: false
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Setting', SettingSchema); 