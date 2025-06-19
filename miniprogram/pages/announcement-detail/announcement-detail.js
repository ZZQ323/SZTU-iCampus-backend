const app = getApp()

Page({
  data: {
    announcement: {},
    loading: true
  },

  onLoad(options) {
    console.log('[公告详情] 页面加载')
    this.loadAnnouncementDetail(options)
  },

  loadAnnouncementDetail(options) {
    // 从全局数据中获取公告信息
    const announcement = app.globalData.currentAnnouncement
    
    if (announcement) {
      this.setData({
        announcement: {
          ...announcement,
          // 格式化时间显示
          fullTime: `${announcement.date} ${announcement.time}`,
          // 添加阅读状态
          isRead: true
        },
        loading: false
      })
      
      console.log('[公告详情] 公告数据加载完成:', announcement.title)
    } else {
      // 如果没有公告数据，返回上一页
      wx.showToast({
        title: '公告数据丢失',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  onBack() {
    wx.navigateBack()
  },

  onShare() {
    const announcement = this.data.announcement
    return {
      title: announcement.title,
      path: `/pages/announcement-detail/announcement-detail`,
      imageUrl: ''
    }
  },

  onCollect() {
    const announcement = this.data.announcement
    
    // 获取已收藏的公告列表
    let collectedAnnouncements = wx.getStorageSync('collectedAnnouncements') || []
    
    // 检查是否已收藏
    const isCollected = collectedAnnouncements.some(item => item.id === announcement.id)
    
    if (isCollected) {
      wx.showToast({
        title: '已经收藏过了',
        icon: 'none'
      })
      return
    }
    
    // 添加到收藏列表
    collectedAnnouncements.unshift({
      ...announcement,
      collectedAt: new Date().toISOString()
    })
    
    // 保存到本地存储（最多保存50条）
    if (collectedAnnouncements.length > 50) {
      collectedAnnouncements = collectedAnnouncements.slice(0, 50)
    }
    
    wx.setStorageSync('collectedAnnouncements', collectedAnnouncements)
    
    wx.showToast({
      title: '收藏成功',
      icon: 'success'
    })
  },

  onCopy() {
    const announcement = this.data.announcement
    const content = `${announcement.title}\n\n${announcement.content}\n\n发布部门：${announcement.department}\n发布时间：${announcement.fullTime}`
    
    wx.setClipboardData({
      data: content,
      success: () => {
        wx.showToast({
          title: '内容已复制',
          icon: 'success'
        })
      }
    })
  }
}) 