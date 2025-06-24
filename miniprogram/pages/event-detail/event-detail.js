const app = getApp()
const API = require('../../utils/api.js')

Page({
  data: {
    event: {},
    loading: true,
    isFollowed: false,
    isRegistered: false
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
        event: event,
        loading: false
      })
      
      // 检查关注和报名状态
      this.checkEventStatus()
      
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

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再进行此操作',
        showCancel: false,
        confirmText: '去登录',
        success: () => {
          wx.navigateTo({
            url: '/pages/login/login'
          })
        }
      })
      return false
    }
    return true
  },

  // 检查活动状态（关注、报名）
  async checkEventStatus() {
    if (!this.checkLoginStatus()) return
    
    try {
      // 这里可以调用API检查用户是否已关注或报名该活动
      // 暂时使用本地存储模拟
      const eventId = this.data.event.id || this.data.event.event_id
      const followedEvents = wx.getStorageSync('followedEvents') || []
      const registeredEvents = wx.getStorageSync('registeredEvents') || []
      
      this.setData({
        isFollowed: followedEvents.includes(eventId),
        isRegistered: registeredEvents.includes(eventId)
      })
    } catch (error) {
      console.error('[活动详情] 检查活动状态失败:', error)
    }
  },

  // 关注/取消关注活动
  async onFollow() {
    if (!this.checkLoginStatus()) return
    
    const eventId = this.data.event.id || this.data.event.event_id
    const isFollowed = this.data.isFollowed
    
    try {
      wx.showLoading({ title: isFollowed ? '取消关注中...' : '关注中...' })
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 更新本地存储
      let followedEvents = wx.getStorageSync('followedEvents') || []
      
      if (isFollowed) {
        // 取消关注
        followedEvents = followedEvents.filter(id => id !== eventId)
        wx.setStorageSync('followedEvents', followedEvents)
        
        this.setData({ isFollowed: false })
        
        wx.hideLoading()
        wx.showToast({
          title: '已取消关注',
          icon: 'success'
        })
      } else {
        // 添加关注
        followedEvents.push(eventId)
        wx.setStorageSync('followedEvents', followedEvents)
        
        this.setData({ isFollowed: true })
        
        wx.hideLoading()
        wx.showToast({
          title: '关注成功',
          icon: 'success'
        })
      }
      
      console.log('[活动详情] 关注状态更新:', isFollowed ? '取消关注' : '已关注')
      
    } catch (error) {
      console.error('[活动详情] 关注操作失败:', error)
      wx.hideLoading()
      wx.showToast({
        title: '操作失败，请重试',
        icon: 'none'
      })
    }
  },

  // 报名/取消报名活动
  async onRegister() {
    if (!this.checkLoginStatus()) return
    
    const { event, isRegistered } = this.data
    const eventId = event.id || event.event_id
    
    if (event.status === 'ended' || event.status === 'cancelled') {
      wx.showToast({
        title: '活动已结束，无法报名',
        icon: 'none'
      })
      return
    }

    if (isRegistered) {
      // 取消报名
      wx.showModal({
        title: '确认取消',
        content: `确定要取消报名"${event.title}"吗？`,
        success: async (res) => {
          if (res.confirm) {
            await this.performRegisterAction(eventId, true)
          }
        }
      })
    } else {
      // 报名参加
      wx.showModal({
        title: '确认报名',
        content: `确定要报名参加"${event.title}"吗？`,
        success: async (res) => {
          if (res.confirm) {
            await this.performRegisterAction(eventId, false)
          }
        }
      })
    }
  },

  // 执行报名操作
  async performRegisterAction(eventId, isCancel) {
    try {
      wx.showLoading({ title: isCancel ? '取消报名中...' : '报名中...' })
      
      // 调用真实API
      let response
      if (isCancel) {
        response = await API.cancelEventRegistration(eventId)
      } else {
        response = await API.registerEvent(eventId)
      }
      
      if (response.code === 0) {
        // 更新本地存储
        let registeredEvents = wx.getStorageSync('registeredEvents') || []
        
        if (isCancel) {
          registeredEvents = registeredEvents.filter(id => id !== eventId)
        } else {
          registeredEvents.push(eventId)
        }
        
        wx.setStorageSync('registeredEvents', registeredEvents)
        
        this.setData({ isRegistered: !isCancel })
        
        wx.hideLoading()
        wx.showToast({
          title: isCancel ? '取消报名成功' : '报名成功',
          icon: 'success'
        })
        
        console.log('[活动详情] 报名状态更新:', isCancel ? '已取消报名' : '已报名')
      } else {
        throw new Error(response.message || '操作失败')
      }
    } catch (error) {
      console.error('[活动详情] 报名操作失败:', error)
      wx.hideLoading()
      wx.showToast({
        title: '操作失败，请重试',
        icon: 'none'
      })
    }
  },

  // 分享活动
  onShare() {
    const { event } = this.data
    
    // 构造分享内容
    const shareContent = `🎯 ${event.title}\n\n📍 地点：${event.location}\n⏰ 时间：${event.startTime}\n👥 主办方：${event.organizer}\n\n${event.description || '精彩活动，期待您的参与！'}`
    
    wx.setClipboardData({
      data: shareContent,
      success: () => {
        wx.showToast({
          title: '活动信息已复制到剪贴板',
          icon: 'success',
          duration: 2000
        })
      }
    })

    // 触发微信分享
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })

    console.log('[活动详情] 分享活动:', event.title)
  },

  // 微信分享配置
  onShareAppMessage() {
    const { event } = this.data
    return {
      title: `🎯 ${event.title}`,
      desc: `📍 ${event.location} | ⏰ ${event.startTime}`,
      path: `/pages/event-detail/event-detail?id=${event.id || event.event_id}`,
      imageUrl: event.image || ''
    }
  },

  // 朋友圈分享配置
  onShareTimeline() {
    const { event } = this.data
    return {
      title: `🎯 ${event.title} | 📍 ${event.location}`,
      query: `id=${event.id || event.event_id}`,
      imageUrl: event.image || ''
    }
  },

  onShow() {
    // 页面显示时重新检查状态
    this.checkEventStatus()
  }
}) 