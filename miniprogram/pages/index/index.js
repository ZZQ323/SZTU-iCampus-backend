const app = getApp()

Page({
  data: {
    announcements: [],
    userInfo: {
      name: '同学你好',
      studentId: '2024XXXXXX'
    }
  },

  onLoad() {
    this.fetchAnnouncements()
    this.getUserInfo()
  },

  async getUserInfo() {
    try {
      // TODO: 从后端获取用户信息
      // const response = await wx.request({
      //   url: 'http://localhost:8000/api/user/info',
      //   method: 'GET'
      // })
      // if (response.statusCode === 200) {
      //   this.setData({
      //     userInfo: response.data
      //   })
      // }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
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
  },

  navigateToGrades() {
    wx.navigateTo({
      url: '/pages/grades/grades'
    })
  },

  navigateToExams() {
    wx.navigateTo({
      url: '/pages/exams/exams'
    })
  },

  navigateToCampusCard() {
    wx.navigateTo({
      url: '/pages/campus-card/campus-card'
    })
  },

  navigateToLibrary() {
    wx.navigateTo({
      url: '/pages/library/library'
    })
  },

  viewAnnouncement(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/announcements/detail?id=${id}`
    })
  }
}) 