const app = getApp()

Page({
  data: {
    announcements: [],
    loading: true
  },

  onLoad() {
    this.fetchAnnouncements()
  },

  onShow() {
    // 页面显示时刷新数据
    this.fetchAnnouncements()
  },

  async fetchAnnouncements() {
    try {
      this.setData({ loading: true })
      
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/announcements`,
          method: 'GET',
          header: {
            'Content-Type': 'application/json'
          },
          success: resolve,
          fail: reject
        })
      })
      
      console.log('公告页API Response:', response)
      
      if (response.statusCode === 200 && response.data.code === 0) {
        this.setData({
          announcements: response.data.data.announcements || []
        })
        console.log('公告页数据已更新:', response.data.data.announcements)
      } else {
        console.error('API返回错误:', response.data)
        wx.showToast({
          title: '获取公告失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('获取公告失败:', error)
      wx.showToast({
        title: '网络连接失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.fetchAnnouncements().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  viewAnnouncement(e) {
    const announcement = e.currentTarget.dataset.announcement
    // 将公告数据存储到全局，供详情页使用
    app.globalData.currentAnnouncement = announcement
    
    wx.showModal({
      title: announcement.title,
      content: announcement.content.length > 100 ? 
        announcement.content.substring(0, 100) + '...' : 
        announcement.content,
      showCancel: true,
      confirmText: '查看详情',
      cancelText: '关闭',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: `/pages/announcements/detail?id=${announcement.id}`
          })
        }
      }
    })
  }
}); 