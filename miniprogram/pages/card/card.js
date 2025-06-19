// 校园卡快速操作面板
Page({
  data: {
    balance: '0.00',
    cardNumber: '2024000000',
    lastUpdateTime: '',
    isLost: false,
    showRechargeDialog: false,
    selectedAmount: 0,
    rechargeOptions: [10, 20, 50, 100, 200, 500]
  },

  onLoad() {
    this.loadCardInfo()
  },

  onShow() {
    this.loadCardInfo()
  },

  // 加载卡片信息
  loadCardInfo() {
    // 获取用户信息
    const userInfo = wx.getStorageSync('userInfo')
    
    // 模拟校园卡数据
    const now = new Date()
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    this.setData({
      balance: '185.50',
      cardNumber: userInfo.studentId || '2024000000',
      lastUpdateTime: `更新时间：${timeStr}`,
      isLost: false
    })
  },

  // 快速充值
  onQuickRecharge() {
    if (this.data.isLost) {
      wx.showToast({
        title: '卡片已挂失，无法充值',
        icon: 'none'
      })
      return
    }
    
    wx.showToast({
      title: '请选择充值金额',
      icon: 'none'
    })
  },

  // 选择充值金额
  onSelectAmount(e) {
    const amount = e.currentTarget.dataset.amount
    this.setData({
      selectedAmount: amount,
      showRechargeDialog: true
    })
  },

  // 确认充值
  onRechargeConfirm() {
    const amount = this.data.selectedAmount
    const currentBalance = parseFloat(this.data.balance)
    const newBalance = currentBalance + amount
    
    this.setData({
      balance: newBalance.toFixed(2),
      showRechargeDialog: false
    })
    
    wx.showToast({
      title: `充值成功 ¥${amount}`,
      icon: 'success'
    })
    
    // 更新时间
    const now = new Date()
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    this.setData({
      lastUpdateTime: `更新时间：${timeStr}`
    })
  },

  // 取消充值
  onRechargeCancel() {
    this.setData({
      showRechargeDialog: false
    })
  },

  // 查看消费记录
  onViewRecords() {
    wx.showModal({
      title: '功能提示',
      content: '消费记录功能正在开发中，请稍后使用',
      showCancel: false
    })
  },

  // 切换挂失状态
  onToggleLost() {
    const action = this.data.isLost ? '解除挂失' : '紧急挂失'
    const content = this.data.isLost ? 
      '确定要解除校园卡挂失状态吗？' : 
      '确定要挂失校园卡吗？挂失后卡片将无法使用！'
    
    wx.showModal({
      title: action,
      content: content,
      success: (res) => {
        if (res.confirm) {
          this.setData({
            isLost: !this.data.isLost
          })
          
          wx.showToast({
            title: `${action}成功`,
            icon: 'success'
          })
          
          // 更新时间
          const now = new Date()
          const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
          this.setData({
            lastUpdateTime: `更新时间：${timeStr}`
          })
        }
      }
    })
  },

  // 查看完整版校园卡
  onViewFullCard() {
    wx.navigateTo({
      url: '/pages/campus-card/campus-card'
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadCardInfo()
    setTimeout(() => {
      wx.stopPullDownRefresh()
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    }, 1000)
  }
}) 