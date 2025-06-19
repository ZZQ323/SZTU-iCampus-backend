const app = getApp()

Page({
  data: {
    event: {},
    loading: true
  },

  onLoad(options) {
    console.log('[活动详情] 页面加载')
    this.loadEventDetail(options)
  },

  loadEventDetail(options) {
    // 从全局数据中获取活动信息
    const event = app.globalData.currentEvent
    
    if (event) {
      this.setData({
        event: {
          ...event,
          // 格式化活动状态
          statusText: this.getEventStatusText(event.status),
          // 格式化活动时间
          timeText: this.formatEventTime(event)
        },
        loading: false
      })
      
      console.log('[活动详情] 活动数据加载完成:', event.title)
    } else {
      // 如果没有活动数据，返回上一页
      wx.showToast({
        title: '活动数据丢失',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  // 获取活动状态文本
  getEventStatusText(status) {
    const statusMap = {
      upcoming: '即将开始',
      ongoing: '进行中',
      ended: '已结束',
      cancelled: '已取消'
    }
    return statusMap[status] || '未知状态'
  },

  // 格式化活动时间
  formatEventTime(event) {
    if (event.startTime && event.endTime) {
      return `${event.startTime} - ${event.endTime}`
    } else if (event.date && event.time) {
      return `${event.date} ${event.time}`
    }
    return '时间待定'
  },

  // 报名参加活动
  registerEvent() {
    const { event } = this.data
    
    if (event.status === 'ended' || event.status === 'cancelled') {
      wx.showToast({
        title: '活动已结束，无法报名',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '确认报名',
      content: `确定要报名参加"${event.title}"吗？`,
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({
            title: '报名中...'
          })
          
          // 模拟报名过程
          setTimeout(() => {
            wx.hideLoading()
            wx.showToast({
              title: '报名成功',
              icon: 'success'
            })
          }, 1500)
        }
      }
    })
  },

  // 复制活动信息
  copyEventInfo() {
    const { event } = this.data
    const eventInfo = `活动：${event.title}\n时间：${event.timeText}\n地点：${event.location}\n主办方：${event.organizer}\n状态：${event.statusText}`
    
    wx.setClipboardData({
      data: eventInfo,
      success: () => {
        wx.showToast({
          title: '活动信息已复制',
          icon: 'success'
        })
      }
    })
  },

  // 分享活动
  shareEvent() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })

    wx.showToast({
      title: '分享功能已开启',
      icon: 'success'
    })
  }
}) 