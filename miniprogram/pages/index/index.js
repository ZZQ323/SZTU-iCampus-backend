const app = getApp()
const { AnnouncementStream, streamManager } = require('../../utils/stream')

Page({
  data: {
    announcements: [],
    userInfo: {
      name: '同学你好',
      studentId: '2024XXXXXX'
    },
    loading: true,
    isStreamConnected: false,  // 流式连接状态
    newAnnouncementCount: 0    // 新公告提醒数量
  },

  onLoad() {
    this.fetchAnnouncements()
    this.getUserInfo()
    // 🔥 启动流式公告推送 - 这是流式封装的核心功能
    this.startAnnouncementStream()
  },

  async getUserInfo() {
    try {
      // TODO: 从后端获取用户信息
      // const response = await wx.request({
      //   url: `${app.globalData.baseUrl}/api/v1/auth/me`,
      //   method: 'GET',
      //   header: {
      //     'Authorization': `Bearer ${wx.getStorageSync('token')}`
      //   }
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
      
      console.log('API Response:', response)
      
      if (response.statusCode === 200 && response.data.code === 0) {
        this.setData({
          announcements: response.data.data.announcements || []
        })
        console.log('公告数据已更新:', response.data.data.announcements)
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

  // 🚀 启动流式公告推送 - 核心流式功能
  startAnnouncementStream() {
    const announcementStream = new AnnouncementStream()
    
    console.log('[首页] 启动流式公告推送...')
    
    announcementStream.start((newAnnouncement) => {
      console.log('[首页] 收到新公告推送:', newAnnouncement)
      
      // 将新公告添加到列表顶部（实时显示）
      const currentAnnouncements = this.data.announcements
      const updatedAnnouncements = [newAnnouncement, ...currentAnnouncements]
      
      this.setData({
        announcements: updatedAnnouncements,
        newAnnouncementCount: this.data.newAnnouncementCount + 1
      })
      
      // 显示新公告提醒
      wx.showToast({
        title: '收到新公告',
        icon: 'none',
        duration: 2000
      })
      
      // 震动提醒
      wx.vibrateShort()
    })
    
    this.setData({ isStreamConnected: true })
    
    // 存储流实例，用于页面销毁时断开连接
    this.announcementStream = announcementStream
  },

  // 停止流式推送
  stopAnnouncementStream() {
    if (this.announcementStream) {
      this.announcementStream.stop()
      this.setData({ isStreamConnected: false })
      console.log('[首页] 停止流式公告推送')
    }
  },

  // 页面显示时重新连接流
  onShow() {
    if (!this.data.isStreamConnected) {
      this.startAnnouncementStream()
    }
  },

  // 页面隐藏时断开流（节省资源）
  onHide() {
    this.stopAnnouncementStream()
  },

  // 页面卸载时断开流
  onUnload() {
    this.stopAnnouncementStream()
  },

  // 清除新公告提醒数量
  clearNewAnnouncementCount() {
    this.setData({ newAnnouncementCount: 0 })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.fetchAnnouncements().then(() => {
      wx.stopPullDownRefresh()
      // 清除新公告提醒
      this.clearNewAnnouncementCount()
    })
  },

  navigateToAnnouncements() {
    wx.switchTab({
      url: '/pages/announcements/announcements'
    })
  },

  navigateToSchedule() {
    wx.switchTab({
      url: '/pages/schedule/schedule'
    })
  },

  navigateToNotices() {
    wx.switchTab({
      url: '/pages/notices/notices'
    })
  },

  navigateToEvents() {
    wx.switchTab({
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
    const announcement = e.currentTarget.dataset.announcement
    // 将公告数据存储到全局，供详情页使用
    app.globalData.currentAnnouncement = announcement
    wx.showModal({
      title: announcement.title,
      content: announcement.content.length > 50 ? 
        announcement.content.substring(0, 50) + '...' : 
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
  },

  onBack() {
    wx.navigateBack({
      delta: 1
    });
  }
}) 