Page({
  data: {
    userInfo: {
      name: '张三',
      studentId: '2024001',
      avatar: '/assets/images/avatar.png'
    },
    balance: '0.00',
    cardNumber: '2024000000',
    recentRecords: []
  },

  onLoad() {
    this.loadCardInfo()
  },

  onBack() {
    wx.navigateBack()
  },

  onRecharge() {
    wx.showModal({
      title: '充值',
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
          // TODO: 调用后端API进行充值
          wx.showLoading({
            title: '充值中...'
          })
          setTimeout(() => {
            wx.hideLoading()
            wx.showToast({
              title: '充值成功',
              icon: 'success'
            })
            this.loadCardInfo()
          }, 1500)
        }
      }
    })
  },

  onViewRecords() {
    wx.navigateTo({
      url: '/pages/campus-card/records/records'
    })
  },

  onReportLoss() {
    wx.showModal({
      title: '挂失确认',
      content: '确定要挂失校园卡吗？',
      success: (res) => {
        if (res.confirm) {
          // TODO: 调用后端API进行挂失
          wx.showLoading({
            title: '处理中...'
          })
          setTimeout(() => {
            wx.hideLoading()
            wx.showToast({
              title: '挂失成功',
              icon: 'success'
            })
          }, 1500)
        }
      }
    })
  },

  loadCardInfo() {
    // TODO: 从后端API获取校园卡信息
    this.setData({
      balance: '100.00',
      recentRecords: [
        {
          id: 1,
          location: '第一食堂',
          time: '2024-03-20 12:30',
          amount: '15.00'
        },
        {
          id: 2,
          location: '图书馆打印',
          time: '2024-03-19 15:45',
          amount: '2.00'
        }
      ]
    })
  }
}); 