const app = getApp()
const API = require('../../utils/api')

Page({
  data: {
    // 用户状态
    userInfo: null,
    isLoggedIn: false,
    
    cardInfo: {
      balance: '0.00',
      cardNumber: '2024000000',
      status: 'normal', // normal, lost, frozen
      lastUpdateTime: '2024-06-20 15:30:25'
    },
    recentRecords: [],
    todaySpending: '0.00',
    monthlySpending: '0.00',
    loading: false,
    
    // 统计数据
    spendingStats: {
      daily: [],
      categories: [],
      locations: []
    },
    
    // 充值方式
    rechargeOptions: [
      { id: 1, name: '支付宝', icon: 'logo-alipay', desc: '支付宝扫码充值', enabled: true },
      { id: 2, name: '微信支付', icon: 'logo-wechat', desc: '微信扫码充值', enabled: true },
      { id: 3, name: '银行卡', icon: 'creditcard', desc: '绑定银行卡充值', enabled: true },
      { id: 4, name: '现金充值', icon: 'wallet', desc: '到校园卡服务点充值', enabled: true }
    ],
    
    // 服务功能
    services: [
      { id: 1, name: '消费记录', icon: 'format-list-bulleted', desc: '查看详细消费记录', url: '/pages/campus-card/records/records' },
      { id: 2, name: '挂失/解挂', icon: 'shield-off', desc: '卡片挂失与解挂', action: 'lossReport' },
      { id: 3, name: '修改密码', icon: 'lock-reset', desc: '修改消费密码', action: 'changePassword' },
      { id: 4, name: '使用指南', icon: 'help-circle', desc: '校园卡使用说明', action: 'showGuide' }
    ]
  },

  onLoad() {
    console.log('[校园卡] 💳 页面加载')
    this.checkLoginStatus()
  },

  onShow() {
    console.log('[校园卡] 页面显示')
    this.checkLoginStatus()
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo
      });
      console.log('[校园卡] 用户已登录:', userInfo);
      this.loadAllData();
    } else {
      this.setData({
        isLoggedIn: false,
        userInfo: null
      });
      this.showLoginPrompt();
    }
  },

  /**
   * 显示登录提示
   */
  showLoginPrompt() {
    wx.showModal({
      title: '需要登录',
      content: '查看校园卡需要先登录，是否前往登录？',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: '/pages/login/login'
          });
        } else {
          wx.switchTab({
            url: '/pages/index/index'
          });
        }
      }
    });
  },

  onPullDownRefresh() {
    console.log('[校园卡] 🔄 下拉刷新')
    this.checkLoginStatus()
    
    setTimeout(() => {
      wx.stopPullDownRefresh()
      wx.showToast({
        title: '刷新完成',
        icon: 'success'
      })
    }, 1500)
  },

  // 加载所有数据
  loadAllData() {
    if (!this.data.isLoggedIn) {
      return;
    }
    this.loadCardInfo()
    this.loadRecentRecords()
    this.loadSpendingStats()
  },

  // 刷新卡片信息
  refreshCardInfo() {
    this.loadCardInfo()
  },

  // 加载校园卡信息
  async loadCardInfo() {
    if (!this.data.userInfo) {
      return;
    }

    this.setData({ loading: true })
    
    try {
      // 调用真实API获取校园卡信息
      const cardData = await API.getCampusCardInfo()
      
      const cardInfo = {
        balance: cardData.card_info?.balance?.toFixed(2) || '0.00',
        cardNumber: cardData.card_info?.card_number || this.data.userInfo.student_id || this.data.userInfo.employee_id,
        status: cardData.card_info?.card_status || 'normal',
        lastUpdateTime: new Date().toLocaleString(),
        ownerName: this.data.userInfo.name,
        ownerType: this.data.userInfo.person_type,
        dailyLimit: cardData.card_info?.daily_limit || 300,
        totalRecharge: cardData.card_info?.total_recharge || 0,
        totalConsumption: cardData.card_info?.total_consumption || 0
      }
      
      this.setData({
        cardInfo: cardInfo,
        loading: false
      })
      
      // 检查余额不足提醒（仅针对学生和教师）
      const balanceNum = parseFloat(cardInfo.balance)
      if ((this.data.userInfo.person_type === 'student' || this.data.userInfo.person_type === 'teacher') && balanceNum < 20) {
        wx.showModal({
          title: '💳 余额不足提醒',
          content: `您的校园卡余额仅剩${cardInfo.balance}元，建议及时充值。`,
          showCancel: true,
          cancelText: '稍后充值',
          confirmText: '立即充值',
          confirmColor: '#0052d9',
          success: (res) => {
            if (res.confirm) {
              this.onRecharge()
            }
          }
        })
      }
    } catch (error) {
      console.error('获取校园卡信息失败:', error)
      this.setData({ loading: false })
      
      // 出错时显示默认信息
      const defaultCardInfo = {
        balance: '0.00',
        cardNumber: this.data.userInfo.student_id || this.data.userInfo.employee_id || 'N/A',
        status: 'normal',
        lastUpdateTime: new Date().toLocaleString(),
        ownerName: this.data.userInfo.name,
        ownerType: this.data.userInfo.person_type
      }
      
      this.setData({
        cardInfo: defaultCardInfo
      })
      
      wx.showToast({
        title: '获取卡片信息失败',
        icon: 'none'
      })
    }
  },

  // 加载近期消费记录
  async loadRecentRecords() {
    if (!this.data.userInfo) {
      return;
    }

    try {
      // 调用真实API获取消费记录
      const transactionData = await API.getTransactions({
        page: 1,
        size: 20,
        sort: 'transaction_time',
        order: 'desc'
      })
      
      // 转换数据格式
      const recentRecords = (transactionData.transactions || []).map(item => ({
        id: item.transaction_id,
        location: item.merchant_name || item.location_name || '未知商户',
        time: item.transaction_time,
        amount: item.transaction_type === 'recharge' ? `+${item.amount}` : `-${item.amount}`,
        balance: item.balance_after?.toFixed(2) || '0.00',
        type: item.transaction_type === 'recharge' ? 'recharge' : 'consume',
        category: this.mapTransactionCategory(item.category, item.merchant_name),
        description: item.description || this.getDefaultDescription(item.transaction_type, item.merchant_name)
      }))
      
      // 计算今日和本月消费
      const today = new Date().toDateString()
      const thisMonth = new Date().getMonth()
      
      let todaySpending = 0
      let monthlySpending = 0
      
      recentRecords.forEach(record => {
        const recordDate = new Date(record.time)
        
        if (record.type === 'consume') {
          const amount = Math.abs(parseFloat(record.amount))
          
          if (recordDate.toDateString() === today) {
            todaySpending += amount
          }
          
          if (recordDate.getMonth() === thisMonth) {
            monthlySpending += amount
          }
        }
      })
      
      this.setData({
        recentRecords: recentRecords,
        todaySpending: todaySpending.toFixed(2),
        monthlySpending: monthlySpending.toFixed(2)
      })
    } catch (error) {
      console.error('获取消费记录失败:', error)
      // 出错时使用空数组
      this.setData({
        recentRecords: [],
        todaySpending: '0.00',
        monthlySpending: '0.00'
      })
    }
  },

  /**
   * 映射交易分类
   */
  mapTransactionCategory(apiCategory, merchantName) {
    const categoryMap = {
      '餐饮': 'dining',
      '购物': 'shopping',
      '图书馆': 'library',
      '其他': 'other'
    }
    
    // 如果API返回了分类，使用映射
    if (apiCategory && categoryMap[apiCategory]) {
      return categoryMap[apiCategory]
    }
    
    // 根据商户名称推断分类
    if (merchantName) {
      if (merchantName.includes('食堂') || merchantName.includes('餐厅')) {
        return 'dining'
      } else if (merchantName.includes('超市') || merchantName.includes('商店')) {
        return 'shopping'
      } else if (merchantName.includes('图书馆') || merchantName.includes('打印')) {
        return 'library'
      } else if (merchantName.includes('咖啡') || merchantName.includes('茶')) {
        return 'coffee'
      }
    }
    
    return 'other'
  },

  /**
   * 获取默认描述
   */
  getDefaultDescription(transactionType, merchantName) {
    if (transactionType === 'recharge') {
      return '校园卡充值'
    }
    
    if (merchantName) {
      if (merchantName.includes('食堂') || merchantName.includes('餐厅')) {
        return '餐饮消费'
      } else if (merchantName.includes('超市')) {
        return '购物消费'
      } else if (merchantName.includes('图书馆')) {
        return '图书馆消费'
      } else if (merchantName.includes('打印')) {
        return '打印费用'
      }
    }
    
    return '校园卡消费'
  },

  // 加载消费统计
  async loadSpendingStats() {
    if (!this.data.userInfo) {
      return;
    }

    try {
      // 调用真实API获取消费统计
      const statsData = await API.getCampusCardStatistics('month')
      
      // 转换数据格式
      const spendingStats = {
        daily: this.processDailyStats(statsData.daily_stats || []),
        categories: this.processCategoryStats(statsData.category_stats || []),
        locations: this.processLocationStats(statsData.location_stats || [])
      }
      
      this.setData({
        spendingStats: spendingStats
      })
    } catch (error) {
      console.error('获取消费统计失败:', error)
      // 出错时使用默认统计
      this.setData({
        spendingStats: {
          daily: [],
          categories: [],
          locations: []
        }
      })
    }
  },

  /**
   * 处理每日统计数据
   */
  processDailyStats(dailyStats) {
    // 获取最近7天的数据
    const last7Days = []
    const today = new Date()
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(today.getDate() - i)
      
      const dateStr = `${date.getMonth() + 1}.${date.getDate()}`
      const dayData = dailyStats.find(item => 
        new Date(item.date).toDateString() === date.toDateString()
      )
      
      last7Days.push({
        date: dateStr,
        amount: dayData ? parseFloat(dayData.amount) : 0
      })
    }
    
    return last7Days
  },

  /**
   * 处理分类统计数据
   */
  processCategoryStats(categoryStats) {
    const colorMap = {
      '餐饮': '#0052d9',
      '购物': '#00a870', 
      '图书馆': '#ff9500',
      '其他': '#e34d59',
      'dining': '#0052d9',
      'shopping': '#00a870',
      'library': '#ff9500',
      'other': '#e34d59'
    }
    
    const totalAmount = categoryStats.reduce((sum, item) => sum + parseFloat(item.amount || 0), 0)
    
    return categoryStats.map(item => ({
      name: item.category_name || item.category,
      amount: parseFloat(item.amount || 0),
      percentage: totalAmount > 0 ? Math.round((parseFloat(item.amount || 0) / totalAmount) * 100) : 0,
      color: colorMap[item.category] || colorMap[item.category_name] || '#666666'
    }))
  },

  /**
   * 处理地点统计数据
   */
  processLocationStats(locationStats) {
    return locationStats.map(item => ({
      name: item.location_name || item.merchant_name || '未知地点',
      count: parseInt(item.transaction_count || 0),
      amount: parseFloat(item.total_amount || 0)
    })).slice(0, 10) // 只显示前10个地点
  },

  // 充值功能
  onRecharge() {
    if (!this.data.isLoggedIn) {
      this.showLoginPrompt();
      return;
    }

    wx.showActionSheet({
      itemList: this.data.rechargeOptions.filter(option => option.enabled).map(option => `${option.name} - ${option.desc}`),
      success: (res) => {
        const selectedOption = this.data.rechargeOptions[res.tapIndex]
        this.handleRecharge(selectedOption)
      }
    })
  },

  // 处理充值
  handleRecharge(option) {
    console.log('[校园卡] 💰 选择充值方式:', option.name)
    
    wx.showModal({
      title: '充值金额',
      content: '请输入充值金额',
      editable: true,
      placeholderText: '请输入金额',
      success: (res) => {
        if (res.confirm && res.content) {
          const amount = parseFloat(res.content)
          if (isNaN(amount) || amount <= 0) {
            wx.showToast({
              title: '请输入有效金额',
              icon: 'none'
            })
            return
          }
          
          if (amount < 1) {
            wx.showToast({
              title: '充值金额不能少于1元',
              icon: 'none'
            })
            return
          }
          
          if (amount > 500) {
            wx.showToast({
              title: '单次充值不能超过500元',
              icon: 'none'
            })
            return
          }
          
          this.processRecharge(option, amount)
        }
      }
    })
  },

  // 处理充值流程
  processRecharge(option, amount) {
    wx.showLoading({
      title: `${option.name}充值中...`
    })
    
    // 模拟充值过程
    setTimeout(() => {
      wx.hideLoading()
      
      // 更新余额
      const currentBalance = parseFloat(this.data.cardInfo.balance)
      const newBalance = (currentBalance + amount).toFixed(2)
      
      this.setData({
        'cardInfo.balance': newBalance,
        'cardInfo.lastUpdateTime': new Date().toLocaleString()
      })
      
      // 添加充值记录
      const newRecord = {
        id: Date.now(),
        location: '充值机',
        time: new Date().toLocaleString(),
        amount: `+${amount.toFixed(2)}`,
        balance: newBalance,
        type: 'recharge',
        category: 'recharge',
        description: `${option.name}充值`
      }
      
      this.setData({
        recentRecords: [newRecord, ...this.data.recentRecords]
      })
      
      wx.showToast({
        title: '充值成功',
        icon: 'success',
        duration: 2000
      })
      
      // 触觉反馈
      wx.vibrateShort()
    }, 2000)
  },

  // 查看消费记录
  onViewRecords() {
    console.log('[校园卡] 📊 查看消费记录')
    wx.navigateTo({
      url: '/pages/campus-card/records/records'
    })
  },

  // 挂失/解挂
  onLossReport() {
    const isLost = this.data.cardInfo.status === 'lost'
    
    wx.showModal({
      title: isLost ? '解除挂失' : '挂失确认',
      content: isLost ? 
        '确定要解除校园卡挂失吗？解挂后卡片将恢复正常使用。' : 
        '确定要挂失校园卡吗？挂失后卡片将无法使用，直到解除挂失。',
      confirmText: isLost ? '解除挂失' : '确认挂失',
      confirmColor: isLost ? '#00a870' : '#e34d59',
      success: (res) => {
        if (res.confirm) {
          this.processLossReport(isLost)
        }
      }
    })
  },

  // 处理挂失流程
  processLossReport(isUnlock = false) {
    wx.showLoading({
      title: isUnlock ? '解除挂失中...' : '挂失处理中...'
    })
    
    setTimeout(() => {
      wx.hideLoading()
      
      this.setData({
        'cardInfo.status': isUnlock ? 'normal' : 'lost',
        'cardInfo.lastUpdateTime': new Date().toLocaleString()
      })
      
      wx.showToast({
        title: isUnlock ? '解除挂失成功' : '挂失成功',
        icon: 'success'
      })
    }, 1500)
  },

  // 修改密码
  onChangePassword() {
    wx.showModal({
      title: '修改消费密码',
      content: '请输入新的6位数字密码',
      editable: true,
      placeholderText: '请输入6位数字',
      success: (res) => {
        if (res.confirm && res.content) {
          const password = res.content.trim()
          
          if (!/^\d{6}$/.test(password)) {
            wx.showToast({
              title: '密码必须为6位数字',
              icon: 'none'
            })
            return
          }
          
          wx.showLoading({
            title: '修改密码中...'
          })
          
          setTimeout(() => {
            wx.hideLoading()
            wx.showToast({
              title: '密码修改成功',
              icon: 'success'
            })
          }, 1000)
        }
      }
    })
  },

  // 显示使用指南
  onShowGuide() {
    const guideContent = `📖 校园卡使用指南

🍽️ 餐饮消费
• 在食堂刷卡消费，支持小额免密支付
• 单笔消费限额：100元
• 日累计消费限额：300元

🏪 商户消费  
• 校内超市、书店等支持校园卡支付
• 部分商户支持扫码支付

💰 充值方式
• 支付宝/微信扫码充值
• 自助充值机现金充值
• 银行卡绑定自动充值

🔒 安全设置
• 小额免密：20元以下免输密码
• 大额消费：需输入6位数字密码
• 遗失及时挂失，避免资金损失

📞 服务热线：0755-12345678
🕐 服务时间：周一至周日 8:00-22:00`

    wx.showModal({
      title: '使用指南',
      content: guideContent,
      showCancel: false,
      confirmText: '我知道了',
      confirmColor: '#0052d9'
    })
  },

  // 服务功能处理
  onServiceTap(e) {
    const service = e.currentTarget.dataset.service
    console.log('[校园卡] 🔧 选择服务:', service.name)
    
    if (service.url) {
      wx.navigateTo({
        url: service.url
      })
    } else if (service.action) {
      switch (service.action) {
        case 'lossReport':
          this.onLossReport()
          break
        case 'changePassword':
          this.onChangePassword()
          break
        case 'showGuide':
          this.onShowGuide()
          break
      }
    }
  },

  // 返回上一页
  onBack() {
    wx.navigateBack()
  }
}) 