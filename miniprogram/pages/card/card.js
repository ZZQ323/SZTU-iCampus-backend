Page({
  data: {
    balance: '0.00',
    cardNumber: '2024000000',
    isLost: false,
    showRechargeDialog: false,
    showPasswordDialog: false,
    rechargeAmount: '',
    newPassword: ''
  },

  onLoad() {
    this.loadCardInfo()
  },

  loadCardInfo() {
    // TODO: 从后端获取校园卡信息
    // 模拟数据
    this.setData({
      balance: '100.00',
      cardNumber: '2024000000',
      isLost: false
    })
  },

  onRecharge() {
    this.setData({
      showRechargeDialog: true,
      rechargeAmount: ''
    })
  },

  onRechargeInput(e) {
    this.setData({
      rechargeAmount: e.detail.value
    })
  },

  onRechargeConfirm() {
    const amount = parseFloat(this.data.rechargeAmount)
    if (isNaN(amount) || amount <= 0) {
      wx.showToast({
        title: '请输入有效金额',
        icon: 'none'
      })
      return
    }

    // TODO: 调用充值接口
    const newBalance = parseFloat(this.data.balance) + amount
    this.setData({
      balance: newBalance.toFixed(2),
      showRechargeDialog: false
    })

    wx.showToast({
      title: '充值成功',
      icon: 'success'
    })
  },

  onRechargeCancel() {
    this.setData({
      showRechargeDialog: false
    })
  },

  onViewRecords() {
    wx.navigateTo({
      url: '/pages/card/records/records'
    })
  },

  onToggleLost() {
    if (this.data.isLost) {
      // 解挂
      wx.showModal({
        title: '解挂确认',
        content: '确定要解除挂失吗？',
        success: (res) => {
          if (res.confirm) {
            // TODO: 调用解挂接口
            this.setData({
              isLost: false
            })
            wx.showToast({
              title: '解挂成功',
              icon: 'success'
            })
          }
        }
      })
    } else {
      // 挂失
      wx.showModal({
        title: '挂失确认',
        content: '确定要挂失校园卡吗？',
        success: (res) => {
          if (res.confirm) {
            // TODO: 调用挂失接口
            this.setData({
              isLost: true
            })
            wx.showToast({
              title: '挂失成功',
              icon: 'success'
            })
          }
        }
      })
    }
  },

  onChangePassword() {
    this.setData({
      showPasswordDialog: true,
      newPassword: ''
    })
  },

  onPasswordInput(e) {
    this.setData({
      newPassword: e.detail.value
    })
  },

  onPasswordConfirm() {
    const password = this.data.newPassword
    if (!password || password.length < 6) {
      wx.showToast({
        title: '密码长度至少6位',
        icon: 'none'
      })
      return
    }

    // TODO: 调用修改密码接口
    this.setData({
      showPasswordDialog: false
    })

    wx.showToast({
      title: '密码修改成功',
      icon: 'success'
    })
  },

  onPasswordCancel() {
    this.setData({
      showPasswordDialog: false
    })
  }
}) 