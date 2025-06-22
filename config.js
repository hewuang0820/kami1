/**
 * 前端配置文件
 */

// API基础URL
// 使用相对路径，通过Nginx反向代理访问后端API
const API_BASE_URL = 'http://170.106.175.187/api';

// API端点
const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: `${API_BASE_URL}/auth/login`,
    INIT: `${API_BASE_URL}/auth/init`,
    ME: `${API_BASE_URL}/auth/me`,
    CHANGE_PASSWORD: `${API_BASE_URL}/auth/change-password`,
  },
  
  // 卡密相关
  CARD_KEYS: {
    BASE: `${API_BASE_URL}/card-keys`,
    GENERATE: `${API_BASE_URL}/card-keys/generate`,
    VERIFY: `${API_BASE_URL}/card-keys/verify`,
    STATISTICS: `${API_BASE_URL}/card-keys/statistics`,
    VERIFICATION_LOGS: `${API_BASE_URL}/card-keys/verification-logs`,
  },
  
  // 系统设置
  SETTINGS: {
    BASE: `${API_BASE_URL}/settings`,
  }
};

// 导出配置
const config = {
  API_BASE_URL,
  API_ENDPOINTS,
  TOKEN_KEY: 'kami_system_token',
  DEFAULT_AVATAR: 'https://via.placeholder.com/100',
  PAGE_SIZE: 10,
};

// 在全局范围内暴露配置
window.APP_CONFIG = config; 