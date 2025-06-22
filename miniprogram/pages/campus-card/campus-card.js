const app = getApp()

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
  loadCardInfo() {
    if (!this.data.userInfo) {
      return;
    }

    this.setData({ loading: true })
    
    const userInfo = this.data.userInfo;
    const cardNumber = userInfo.student_id || userInfo.employee_id || userInfo.login_id;
    
    // 模拟API请求
    setTimeout(() => {
      // 根据用户类型生成不同的余额
      let balance = '156.78'; // 默认余额
      if (userInfo.person_type === 'student') {
        balance = (Math.random() * 500 + 50).toFixed(2); // 学生50-550元
      } else if (userInfo.person_type === 'teacher') {
        balance = (Math.random() * 200 + 100).toFixed(2); // 教师100-300元
      } else if (userInfo.person_type === 'admin') {
        balance = (Math.random() * 100 + 200).toFixed(2); // 管理员200-300元
      }

      const mockCardInfo = {
        balance: balance,
        cardNumber: cardNumber,
        status: 'normal',
        lastUpdateTime: new Date().toLocaleString(),
        ownerName: userInfo.name,
        ownerType: userInfo.person_type
      }
      
      this.setData({
        cardInfo: mockCardInfo,
        loading: false
      })
      
      // 检查余额不足提醒（仅针对学生和教师）
      const balanceNum = parseFloat(mockCardInfo.balance)
      if ((userInfo.person_type === 'student' || userInfo.person_type === 'teacher') && balanceNum < 20) {
        wx.showModal({
          title: '💳 余额不足提醒',
          content: `您的校园卡余额仅剩${mockCardInfo.balance}元，建议及时充值。`,
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
    }, 800)
  },

  // 加载近期消费记录
  loadRecentRecords() {
    if (!this.data.userInfo) {
      return;
    }

    const userType = this.data.userInfo.person_type;
    let mockRecords = [];

    if (userType === 'student') {
      // 学生消费记录：主要是食堂、超市、图书馆
      mockRecords = [
        {
          id: 1,
          location: '第一食堂',
          time: '2024-06-20 12:30:15',
          amount: '-15.50',
          balance: '156.78',
          type: 'consume',
          category: 'dining',
          description: '午餐消费'
        },
        {
          id: 2,
          location: '图书馆打印室',
          time: '2024-06-20 10:45:22',
          amount: '-2.50',
          balance: '171.78',
          type: 'consume',
          category: 'printing',
          description: '打印费用'
        },
        {
          id: 3,
          location: '充值机',
          time: '2024-06-19 18:20:10',
          amount: '+50.00',
          balance: '174.28',
          type: 'recharge',
          category: 'recharge',
          description: '支付宝充值'
        },
        {
          id: 4,
          location: '第二食堂',
          time: '2024-06-19 18:15:33',
          amount: '-18.50',
          balance: '124.28',
          type: 'consume',
          category: 'dining',
          description: '晚餐消费'
        }
      ];
    } else if (userType === 'teacher' || userType === 'assistant_teacher') {
      // 教师消费记录：食堂、咖啡、打印等
      mockRecords = [
        {
          id: 1,
          location: '教师餐厅',
          time: '2024-06-20 12:00:00',
          amount: '-25.00',
          balance: '275.50',
          type: 'consume',
          category: 'dining',
          description: '午餐消费'
        },
        {
          id: 2,
          location: '咖啡厅',
          time: '2024-06-20 09:30:15',
          amount: '-18.00',
          balance: '300.50',
          type: 'consume',
          category: 'coffee',
          description: '咖啡消费'
        },
        {
          id: 3,
          location: '打印服务中心',
          time: '2024-06-19 16:20:10',
          amount: '-12.00',
          balance: '318.50',
          type: 'consume',
          category: 'printing',
          description: '打印课件'
        }
      ];
    } else {
      // 管理员等其他人员的记录较少
      mockRecords = [
        {
          id: 1,
          location: '行政餐厅',
          time: '2024-06-20 12:30:00',
          amount: '-30.00',
          balance: '270.00',
          type: 'consume',
          category: 'dining',
          description: '工作餐'
        },
        {
          id: 2,
          location: '充值机',
          time: '2024-06-18 09:00:00',
          amount: '+100.00',
          balance: '300.00',
          type: 'recharge',
          category: 'recharge',
          description: '银行卡充值'
        }
      ];
    }
    
    // 计算今日和本月消费
    const today = new Date().toDateString()
    const thisMonth = new Date().getMonth()
    
    let todaySpending = 0
    let monthlySpending = 0
    
    mockRecords.forEach(record => {
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
      recentRecords: mockRecords,
      todaySpending: todaySpending.toFixed(2),
      monthlySpending: monthlySpending.toFixed(2)
    })
  },

  // 加载消费统计
  loadSpendingStats() {
    if (!this.data.userInfo) {
      return;
    }

    const userType = this.data.userInfo.person_type;
    let mockStats = {};

    if (userType === 'student') {
      mockStats = {
        daily: [
          { date: '6.16', amount: 25.5 },
          { date: '6.17', amount: 31.2 },
          { date: '6.18', amount: 18.8 },
          { date: '6.19', amount: 42.1 },
          { date: '6.20', amount: 17.5 }
        ],
        categories: [
          { name: '餐饮', amount: 89.5, percentage: 65, color: '#0052d9' },
          { name: '购物', amount: 28.3, percentage: 20, color: '#00a870' },
          { name: '打印', amount: 12.8, percentage: 10, color: '#ff9500' },
          { name: '其他', amount: 6.5, percentage: 5, color: '#e34d59' }
        ],
        locations: [
          { name: '第一食堂', count: 15, amount: 245.6 },
          { name: '第二食堂', count: 8, amount: 156.3 },
          { name: '超市', count: 5, amount: 67.9 },
          { name: '图书馆', count: 12, amount: 24.5 }
        ]
      };
    } else if (userType === 'teacher' || userType === 'assistant_teacher') {
      mockStats = {
        daily: [
          { date: '6.16', amount: 45.0 },
          { date: '6.17', amount: 38.5 },
          { date: '6.18', amount: 52.3 },
          { date: '6.19', amount: 41.2 },
          { date: '6.20', amount: 43.0 }
        ],
        categories: [
          { name: '餐饮', amount: 125.0, percentage: 55, color: '#0052d9' },
          { name: '咖啡茶饮', amount: 68.0, percentage: 30, color: '#00a870' },
          { name: '打印复印', amount: 24.0, percentage: 10, color: '#ff9500' },
          { name: '其他', amount: 11.0, percentage: 5, color: '#e34d59' }
        ],
        locations: [
          { name: '教师餐厅', count: 12, amount: 320.0 },
          { name: '咖啡厅', count: 8, amount: 156.0 },
          { name: '打印中心', count: 3, amount: 36.0 }
        ]
      };
    } else {
      mockStats = {
        daily: [
          { date: '6.16', amount: 30.0 },
          { date: '6.17', amount: 25.0 },
          { date: '6.18', amount: 35.0 },
          { date: '6.19', amount: 28.0 },
          { date: '6.20', amount: 30.0 }
        ],
        categories: [
          { name: '餐饮', amount: 148.0, percentage: 100, color: '#0052d9' }
        ],
        locations: [
          { name: '行政餐厅', count: 5, amount: 148.0 }
        ]
      };
    }
    
    this.setData({
      spendingStats: mockStats
    })
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