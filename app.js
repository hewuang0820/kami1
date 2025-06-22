/**
 * 卡密验证系统前端脚本
 * 使用Vue.js实现交互逻辑
 */

// 初始化Vue应用
new Vue({
  el: '#app',
  data: {
    // 管理员登录
    isAdminLoggedIn: false,
    showLoginModal: false,
    adminCredentials: {
      username: '',
      password: ''
    },
    loginError: false,
    
    // 管理员后台
    activeNav: 'cards',
    mockCards: [], // 将从API获取
    cardSearch: '',
    generateCount: 5,
    generateValidity: 30,
    customValidityDays: 1, // 新增自定义有效期天数
    generateCardType: '时长卡',
    statistics: {
      total: 0,
      used: 0,
      unused: 0,
      expired: 0
    },
    
    // 使用记录
    verificationLogs: [],
    
    // 系统设置
    settings: {
      systemName: '卡密验证系统',
      adminEmail: 'admin@example.com',
      keyFormat: 'XXXX-XXXX-XXXX-XXXX'
    },
    passwordChange: {
      current: '',
      new: '',
      confirm: ''
    },
    
    // 提示消息
    toast: {
      show: false,
      message: '',
      type: 'info'
    },
    
    // 分页
    pagination: {
      currentPage: 1,
      totalPages: 1,
      totalItems: 0
    },
    
    // 验证记录分页
    logsPagination: {
      currentPage: 1,
      totalPages: 1,
      totalItems: 0
    },
    
    // API状态
    loading: false,
    error: null
  },
  
  computed: {
    // 筛选卡密列表
    filteredCards() {
      if (!this.cardSearch) {
        return this.mockCards;
      }
      
      const search = this.cardSearch.toLowerCase();
      return this.mockCards.filter(card => 
        card.key.toLowerCase().includes(search) || 
        card.status.toLowerCase().includes(search)
      );
    },
    
    // 获取认证令牌
    token() {
      return localStorage.getItem(window.APP_CONFIG.TOKEN_KEY);
    },
    
    // 请求头配置
    requestConfig() {
      return {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.token ? `Bearer ${this.token}` : ''
        }
      };
    }
  },
  
  watch: {
    // 监听导航切换
    activeNav(newValue) {
      if (newValue === 'stats') {
        this.$nextTick(() => {
          this.initCharts();
        });
      }
    }
  },
  
  methods: {
    /**
     * 显示管理员登录模态窗
     */
    showAdminLogin() {
      this.showLoginModal = true;
      this.adminCredentials = {
        username: '',
        password: ''
      };
      this.loginError = false;
    },
    
    /**
     * 管理员登录验证
     */
    async adminLogin() {
      try {
        this.loading = true;
        
        // 发送登录请求
        const response = await axios.post(
          window.APP_CONFIG.API_ENDPOINTS.AUTH.LOGIN, 
          this.adminCredentials
        );
        
        // 处理响应
        if (response.data.success) {
          // 保存token
          localStorage.setItem(window.APP_CONFIG.TOKEN_KEY, response.data.token);
          
          // 更新状态
          this.isAdminLoggedIn = true;
          this.showLoginModal = false;
          this.showToast('登录成功！', 'success');
          
          // 初始化数据
          this.fetchCardKeys();
          this.fetchStatistics();
          this.fetchSettings();
          this.fetchVerificationLogs();
          
          // 初始化图表
          this.$nextTick(() => {
            this.initCharts();
          });
        }
      } catch (error) {
        console.error('Login error:', error);
        this.loginError = true;
        
        if (error.response && error.response.data) {
          this.showToast(error.response.data.message || '登录失败', 'error');
        } else {
          this.showToast('登录失败，请稍后重试', 'error');
        }
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 退出登录
     */
    logout() {
      localStorage.removeItem(window.APP_CONFIG.TOKEN_KEY);
      this.isAdminLoggedIn = false;
      this.showToast('已退出登录', 'info');
    },
    
    /**
     * 获取卡密列表
     */
    async fetchCardKeys() {
      try {
        this.loading = true;
        
        // 构建请求URL
        const params = new URLSearchParams();
        params.append('page', this.pagination.currentPage);
        params.append('limit', window.APP_CONFIG.PAGE_SIZE);
        
        if (this.cardSearch) {
          params.append('search', this.cardSearch);
        }
        
        // 发送请求
        const response = await axios.get(
          `${window.APP_CONFIG.API_ENDPOINTS.CARD_KEYS.BASE}?${params.toString()}`, 
          this.requestConfig
        );
        
        // 处理响应
        if (response.data.success) {
          this.mockCards = response.data.data;
          this.pagination.totalPages = response.data.pages;
          this.pagination.totalItems = response.data.total;
        }
      } catch (error) {
        console.error('Fetch card keys error:', error);
        this.error = error.response?.data?.message || '获取卡密列表失败';
        this.showToast(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 获取统计数据
     */
    async fetchStatistics() {
      try {
        this.loading = true;
        
        // 发送请求
        const response = await axios.get(
          window.APP_CONFIG.API_ENDPOINTS.CARD_KEYS.STATISTICS, 
          this.requestConfig
        );
        
        // 处理响应
        if (response.data.success) {
          this.statistics = response.data.data;
          
          // 如果当前在统计页面，更新或初始化图表
          if (this.activeNav === 'stats') {
            if (this.chart) {
              this.updateCharts();
            } else {
              this.$nextTick(() => {
                this.initCharts();
              });
            }
          }
        }
      } catch (error) {
        console.error('Fetch statistics error:', error);
        this.error = error.response?.data?.message || '获取统计数据失败';
        this.showToast(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 获取系统设置
     */
    async fetchSettings() {
      try {
        this.loading = true;
        
        // 发送请求
        const response = await axios.get(
          window.APP_CONFIG.API_ENDPOINTS.SETTINGS.BASE, 
          this.requestConfig
        );
        
        // 处理响应
        if (response.data.success) {
          this.settings = response.data.data;
        }
      } catch (error) {
        console.error('Fetch settings error:', error);
        this.error = error.response?.data?.message || '获取系统设置失败';
        this.showToast(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 获取验证记录
     */
    async fetchVerificationLogs() {
      try {
        this.loading = true;
        
        // 构建请求URL
        const params = new URLSearchParams();
        params.append('page', this.logsPagination.currentPage);
        params.append('limit', window.APP_CONFIG.PAGE_SIZE);
        
        // 发送请求
        const response = await axios.get(
          `${window.APP_CONFIG.API_ENDPOINTS.CARD_KEYS.VERIFICATION_LOGS}?${params.toString()}`, 
          this.requestConfig
        );
        
        // 处理响应
        if (response.data.success) {
          this.verificationLogs = response.data.data;
          this.logsPagination.totalPages = response.data.pages;
          this.logsPagination.totalItems = response.data.total;
        }
      } catch (error) {
        console.error('Fetch verification logs error:', error);
        this.error = error.response?.data?.message || '获取验证记录失败';
        this.showToast(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 删除卡密
     */
    async deleteCard(id) {
      // 确认删除
      if (!confirm('确定要删除此卡密吗？')) {
        return;
      }
      
      try {
        this.loading = true;
        
        // 发送请求
        const response = await axios.delete(
          `${window.APP_CONFIG.API_ENDPOINTS.CARD_KEYS.BASE}/${id}`, 
          this.requestConfig
        );
        
        // 处理响应
        if (response.data.success) {
          this.showToast('卡密已删除', 'success');
          
          // 刷新数据
          this.fetchCardKeys();
          this.fetchStatistics();
        }
      } catch (error) {
        console.error('Delete card error:', error);
        this.error = error.response?.data?.message || '删除卡密失败';
        this.showToast(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 导出卡密列表
     */
    exportCards() {
      // 简单实现：将当前显示的卡密导出为CSV
      if (this.mockCards.length === 0) {
        this.showToast('没有数据可导出', 'error');
        return;
      }
      
      // 创建CSV内容
      const headers = ['ID', '卡密', '状态', '创建时间', '使用时间', '有效期(天)'];
      const csvContent = [
        headers.join(','),
        ...this.mockCards.map(card => [
          card._id,
          card.key,
          card.status,
          new Date(card.createTime).toLocaleDateString(),
          card.useTime ? new Date(card.useTime).toLocaleString() : '-',
          card.validDays
        ].join(','))
      ].join('\n');
      
      // 创建下载链接
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `卡密列表_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      this.showToast('卡密列表已导出', 'success');
    },
    
    /**
     * 生成新卡密
     */
    async generateCards() {
      // 确认生成
      if (!confirm(`确定要生成 ${this.generateCount} 张卡密吗？`)) {
        return;
      }
      
      try {
        this.loading = true;
        
        // 准备请求数据
        const data = {
          count: parseInt(this.generateCount),
          validDays: this.generateValidity === 'custom' ? parseInt(this.customValidityDays) : parseInt(this.generateValidity),
          format: this.settings.keyFormat,
          cardType: this.generateCardType
        };
      
        // 发送请求
        const response = await axios.post(
          window.APP_CONFIG.API_ENDPOINTS.CARD_KEYS.GENERATE, 
          data,
          this.requestConfig
        );
      
        // 处理响应
        if (response.data.success) {
          this.showToast(response.data.message || `成功生成 ${this.generateCount} 张卡密`, 'success');
          
          // 刷新数据
          this.fetchCardKeys();
          this.fetchStatistics();
        }
      } catch (error) {
        console.error('Generate cards error:', error);
        this.error = error.response?.data?.message || '生成卡密失败';
        this.showToast(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 保存系统设置
     */
    async saveSettings() {
      try {
        this.loading = true;
        
        // 发送请求
        const response = await axios.put(
          window.APP_CONFIG.API_ENDPOINTS.SETTINGS.BASE, 
          this.settings,
          this.requestConfig
        );
        
        // 处理响应
        if (response.data.success) {
      this.showToast('系统设置已保存', 'success');
          this.settings = response.data.data;
        }
      } catch (error) {
        console.error('Save settings error:', error);
        this.error = error.response?.data?.message || '保存系统设置失败';
        this.showToast(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 修改密码
     */
    async changePassword() {
      // 简单验证
      if (!this.passwordChange.current || 
          !this.passwordChange.new || 
          !this.passwordChange.confirm) {
        this.showToast('请填写所有密码字段', 'error');
        return;
      }
      
      // 检查两次输入是否一致
      if (this.passwordChange.new !== this.passwordChange.confirm) {
        this.showToast('两次输入的新密码不一致', 'error');
        return;
      }
      
      try {
        this.loading = true;
        
        // 准备请求数据
        const data = {
          currentPassword: this.passwordChange.current,
          newPassword: this.passwordChange.new
        };
        
        // 发送请求
        const response = await axios.put(
          window.APP_CONFIG.API_ENDPOINTS.AUTH.CHANGE_PASSWORD, 
          data,
          this.requestConfig
        );
        
        // 处理响应
        if (response.data.success) {
      this.showToast('密码修改成功', 'success');
      
      // 重置表单
      this.passwordChange = {
        current: '',
        new: '',
        confirm: ''
      };
        }
      } catch (error) {
        console.error('Change password error:', error);
        this.error = error.response?.data?.message || '修改密码失败';
        this.showToast(this.error, 'error');
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 显示提示消息
     */
    showToast(message, type = 'info') {
      // 清除现有计时器
      if (this.toastTimer) {
        clearTimeout(this.toastTimer);
      }
      
      // 设置新提示
      this.toast = {
        show: true,
        message,
        type
      };
      
      // 自动隐藏
      this.toastTimer = setTimeout(() => {
        this.toast.show = false;
      }, 3000);
    },
    
    /**
     * 初始化图表
     */
    initCharts() {
      // 先检查元素是否存在
      const chartElement = document.getElementById('cardStatusChart');
      if (!chartElement) {
        console.log('图表元素不存在，无法初始化图表');
        return;
      }
      
      // 销毁旧图表
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
      
      const ctx = chartElement.getContext('2d');
      
      this.chart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['已使用', '未使用', '已过期'],
          datasets: [{
            data: [
              this.statistics.used,
              this.statistics.unused,
              this.statistics.expired
            ],
            backgroundColor: [
              '#1FB8CD',
              '#FFC185',
              '#B4413C'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 20,
                boxWidth: 15
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.raw;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        }
      });
    },
    
    /**
     * 更新图表数据
     */
    updateCharts() {
      if (this.chart) {
        this.chart.data.datasets[0].data = [
          this.statistics.used,
          this.statistics.unused,
          this.statistics.expired
        ];
        this.chart.update();
      }
    },

    /**
     * 检查本地存储的登录状态
     */
    checkLoginStatus() {
      const token = localStorage.getItem(window.APP_CONFIG.TOKEN_KEY);
      if (token) {
        this.isAdminLoggedIn = true;
        
        // 加载数据
        this.fetchCardKeys();
        this.fetchStatistics();
        this.fetchSettings();
        this.fetchVerificationLogs();
        
        // 初始化图表
        this.$nextTick(() => {
          this.initCharts();
        });
      }
    },
    
    /**
     * 初始化系统（仅首次使用）
     */
    async initSystem() {
      try {
        // 检查是否有管理员账号
        const response = await axios.post(window.APP_CONFIG.API_ENDPOINTS.AUTH.INIT);
        
        if (response.data.success) {
          this.showToast('系统初始化成功，请使用默认账号登录', 'success');
        }
      } catch (error) {
        // 如果返回400，说明已经初始化过，这是正常情况
        if (error.response && error.response.status === 400) {
          console.log('系统已经初始化过');
        } else {
          console.error('Init system error:', error);
        }
      }
    },
    
    /**
     * 分页切换
     */
    changePage(page) {
      if (page < 1 || page > this.pagination.totalPages) return;
      this.pagination.currentPage = page;
      this.fetchCardKeys();
    },
    
    /**
     * 切换验证记录分页
     */
    changeLogsPage(page) {
      if (page >= 1 && page <= this.logsPagination.totalPages) {
        this.logsPagination.currentPage = page;
        this.fetchVerificationLogs();
      }
    }
  },
  
  mounted() {
    // 检查登录状态
    this.checkLoginStatus();
    
    // 如果已登录，初始化数据
    if (this.isAdminLoggedIn) {
      this.fetchCardKeys();
      this.fetchStatistics();
      this.fetchSettings();
      this.fetchVerificationLogs();
      
      // 初始化图表
      this.$nextTick(() => {
        this.initCharts();
      });
    }
  }
});