// 校园卡快速操作面板
const API = require('../../utils/api.js')

Page({
  data: {
    balance: '0.00',
    cardNumber: '2024000000',
    lastUpdateTime: '',
    isLost: false,
    showRechargeDialog: false,
    selectedAmount: 0,
    rechargeOptions: [10, 20, 50, 100, 200, 500],
    loading: false
  },

  onLoad() {
    this.loadCardInfo()
  },

  onShow() {
    this.loadCardInfo()
  },

  // 加载卡片信息
  async loadCardInfo() {
    this.setData({ loading: true })
    
    try {
      const response = await API.getCampusCardInfo()
      
      if (response.code === 0) {
        const cardInfo = response.data || {}
        const now = new Date()
        const timeStr = now.toLocaleTimeString()
        
        this.setData({
          balance: (cardInfo.balance || 0).toFixed(2),
          cardNumber: cardInfo.card_number || '未知',
          lastUpdateTime: `更新时间：${timeStr}`,
          isLost: cardInfo.status === 'lost',
          loading: false
        })
      } else {
        throw new Error(response.message || '获取校园卡信息失败')
      }
    } catch (error) {
      console.error('[校园卡快速面板] ❌ 加载卡片信息失败:', error)
      this.setData({ loading: false })
      
      // 获取用户信息作为备用显示
    const userInfo = wx.getStorageSync('userInfo')
    const now = new Date()
      const timeStr = now.toLocaleTimeString()
    
    this.setData({
        balance: '0.00',
        cardNumber: userInfo?.student_id || '未知',
      lastUpdateTime: `更新时间：${timeStr}`,
      isLost: false
    })
      
      wx.showToast({
        title: '加载失败，显示默认信息',
        icon: 'none'
      })
    }
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
  async onRechargeConfirm() {
    const amount = this.data.selectedAmount
    
    try {
      wx.showLoading({ title: '充值中...' })
      
      const response = await API.rechargeCampusCard({
        amount: amount
      })
      
      if (response.code === 0) {
        wx.hideLoading()
        
        // 更新余额
        this.loadCardInfo()
    
    this.setData({
      showRechargeDialog: false
    })
    
    wx.showToast({
      title: `充值成功 ¥${amount}`,
      icon: 'success'
    })
      } else {
        throw new Error(response.message || '充值失败')
      }
    } catch (error) {
      console.error('[校园卡快速面板] ❌ 充值失败:', error)
      wx.hideLoading()
      wx.showToast({
        title: '充值失败，请重试',
        icon: 'none'
      })
    }
  },

  // 取消充值
  onRechargeCancel() {
    this.setData({
      showRechargeDialog: false
    })
  },

  // 查看消费记录
  onViewRecords() {
    wx.navigateTo({
      url: '/pages/campus-card/campus-card?tab=transactions'
    })
  },

  // 切换挂失状态
  async onToggleLost() {
    const action = this.data.isLost ? '解除挂失' : '紧急挂失'
    const content = this.data.isLost ? 
      '确定要解除校园卡挂失状态吗？' : 
      '确定要挂失校园卡吗？挂失后卡片将无法使用！'
    
    wx.showModal({
      title: action,
      content: content,
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: `${action}中...` })
            
            const response = await API.toggleCampusCardLost({
              action: this.data.isLost ? 'unlock' : 'lock'
            })
            
            if (response.code === 0) {
              wx.hideLoading()
              
          this.setData({
            isLost: !this.data.isLost
          })
          
          wx.showToast({
            title: `${action}成功`,
            icon: 'success'
          })
          
              // 刷新卡片信息
              this.loadCardInfo()
            } else {
              throw new Error(response.message || `${action}失败`)
            }
          } catch (error) {
            console.error(`[校园卡快速面板] ❌ ${action}失败:`, error)
            wx.hideLoading()
            wx.showToast({
              title: `${action}失败，请重试`,
              icon: 'none'
            })
          }
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