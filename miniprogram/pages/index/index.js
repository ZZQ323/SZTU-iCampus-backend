const app = getApp()

Page({
  data: {
    announcements: []
  },

  onLoad() {
    this.fetchAnnouncements()
  },

  async fetchAnnouncements() {
    try {
      const response = await wx.request({
        url: 'http://localhost:8000/api/announcements',
        method: 'GET'
      })
      
      if (response.statusCode === 200) {
        this.setData({
          announcements: response.data.announcements
        })
      }
    } catch (error) {
      console.error('获取公告失败:', error)
      wx.showToast({
        title: '获取公告失败',
        icon: 'none'
      })
    }
  },

  navigateToAnnouncements() {
    wx.navigateTo({
      url: '/pages/announcements/announcements'
    })
  },

  navigateToSchedule() {
    wx.navigateTo({
      url: '/pages/schedule/schedule'
    })
  },

  navigateToNotices() {
    wx.navigateTo({
      url: '/pages/notices/notices'
    })
  },

  navigateToEvents() {
    wx.navigateTo({
      url: '/pages/events/events'
    })
  }
}) 