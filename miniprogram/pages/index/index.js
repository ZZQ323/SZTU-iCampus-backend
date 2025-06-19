const app = getApp()
const { announcementStream, streamManager } = require('../../utils/stream.js')

Page({
  data: {
    userInfo: {},
    announcements: [],
    newAnnouncementCount: 0,
    quickServices: [
      { title: '公告', icon: '📢', path: '/pages/announcements/announcements' },
      { title: '课表', icon: '📅', path: '/pages/schedule/schedule' },
      { title: '通知', icon: '📋', path: '/pages/notifications/notifications' },
      { title: '活动', icon: '🎯', path: '/pages/events/events' },
      { title: '成绩', icon: '📊', path: '/pages/grades/grades' },
      { title: '考试', icon: '📝', path: '/pages/exams/exams' },
      { title: '校园卡', icon: '💳', path: '/pages/campus-card/campus-card' },
      { title: '图书馆', icon: '📚', path: '/pages/library/library' }
    ],
    // 后勤联系电话
    contactInfo: [
      { name: '校医院', phone: '0755-26731120', icon: '🏥', category: '医疗' },
      { name: '保卫处', phone: '0755-26731110', icon: '🚔', category: '安全' },
      { name: '后勤服务中心', phone: '0755-26731130', icon: '🔧', category: '维修' },
      { name: '学生宿舍管理', phone: '0755-26731140', icon: '🏠', category: '住宿' },
      { name: '食堂服务热线', phone: '0755-26731150', icon: '🍽️', category: '餐饮' },
      { name: '网络信息中心', phone: '0755-26731160', icon: '💻', category: '网络' },
      { name: '教务处', phone: '0755-26731170', icon: '📚', category: '教务' },
      { name: '学生处', phone: '0755-26731180', icon: '👥', category: '学务' }
    ],
    loading: true,
    streamStatus: {
      isConnected: false,
      connectionTime: ''
    },
    notices: [],
    recentEvents: [],
    user: {
      name: '校园用户',
      studentId: '2024XXXXX',
      avatar: 'assets/test/man.png'
    },
    loadingNotices: false,
    experienceStats: {
      realTimePushes: 0,
      cacheHits: 0,
      networkAdaptations: 0,
      offlineRecoveries: 0
    },
    demoMode: false,
    streamConnectTime: null,
    showDialog: false,
    dialogData: {
      title: '',
      content: ''
    }
  },

  onLoad() {
    console.log('[首页] 🏠 页面加载')
    this.getUserInfo()
    this.fetchAnnouncements()
    this.startStreamExperience()
  },

  onShow() {
    console.log('[首页] 页面显示')
    // 每次显示页面时更新用户信息
    this.getUserInfo()
    // 页面重新显示时更新状态
    this.updateStreamStatus()
  },

  onHide() {
    console.log('[首页] 页面隐藏')
    // 停止流式推送以节省资源
    this.stopAnnouncementStream() // 这tmd没实现
  },

  onUnload() {
    console.log('[首页] 👋 页面卸载，清理流式连接')
    
    // 清理定时器
    if (this.streamStatusUpdater) {
      clearInterval(this.streamStatusUpdater)
    }
    
    // 停止流式连接
    const { announcementStream } = require('../../utils/stream.js')
    announcementStream.stop()
  },

  /**
   * 🔄 清除新公告计数
   */
  clearNewAnnouncementCount() {
    this.setData({
      newAnnouncementCount: 0
    })
  },

  onPullDownRefresh() {
    console.log('[首页] 下拉刷新')
    this.getUserInfo()
    this.fetchAnnouncements()
    
    setTimeout(() => {
      wx.stopPullDownRefresh()
      this.clearNewAnnouncementCount()
    }, 1000)
  },

  // 导航方法
  navigateToService(e) {
    const item = e.currentTarget.dataset.item
    if (!item || !item.path) return
    
    console.log('[首页] 🎯 导航到服务:', item.title, item.path)
    
    // 如果是公告页面，清除新公告计数
    if (item.title === '公告') {
      this.clearNewAnnouncementCount()
    }
    
    // Tab页面需要使用switchTab，普通页面使用navigateTo
    const tabPages = [
      '/pages/index/index',
      '/pages/announcements/announcements', 
      '/pages/schedule/schedule',
      '/pages/address_book/address_book',
      '/pages/campus-card/campus-card'
    ]
    
    if (tabPages.includes(item.path)) {
      wx.switchTab({
        url: item.path,
        fail: (error) => {
          console.error('[首页] Tab导航失败:', error)
          wx.showToast({
            title: `${item.title}页面暂未开放`,
            icon: 'none'
          })
        }
      })
    } else {
      wx.navigateTo({
        url: item.path,
        fail: (error) => {
          console.error('[首页] 普通导航失败:', error)
          wx.showToast({
            title: `${item.title}页面暂未开放`,
            icon: 'none'
          })
        }
      })
    }
  },

  navigateToAnnouncements() {
    this.clearNewAnnouncementCount()
    wx.switchTab({
      url: '/pages/announcements/announcements'
    })
  },

  navigateToSchedule() {
    wx.switchTab({
      url: '/pages/schedule/schedule'
    })
  },

  navigateToAddressBook() {
    wx.switchTab({
      url: '/pages/address_book/address_book'
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

  /**
   * 导航到登录页面
   */
  navigateToLogin() {
    console.log('[首页] 🔑 跳转到登录页面')
    wx.navigateTo({
      url: '/pages/login/login'
    })
  },

  /**
   * 查看公告详情 - 跳转到详情页面
   */
  viewAnnouncementDetail(e) {
    const announcement = e.currentTarget.dataset.announcement
    console.log('[首页] 📄 查看公告详情:', announcement.title)
    
    // 将公告数据存储到全局数据中
    app.globalData.currentAnnouncement = announcement
    
    wx.navigateTo({
      url: '/pages/announcement-detail/announcement-detail'
    })
  },

  /**
   * 导航到管理员页面
   */
  navigateToAdmin() {
    console.log('[首页] 🔧 跳转到管理员页面')
    wx.navigateTo({
      url: '/pages/admin/admin',
      fail: () => {
        wx.showToast({
          title: '页面暂未开放',
          icon: 'none'
        })
      }
    })
  },

  // 退出登录
  onLogout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除本地存储的用户信息
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          
          // 重置页面数据
          this.setData({
            userInfo: {}
          })
          
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          })
        }
      }
    })
  },

  // 获取用户信息
  getUserInfo() {
    try {
      const token = wx.getStorageSync('token')
      const userInfo = wx.getStorageSync('userInfo')
      
      if (userInfo && token) {
        this.setData({
          userInfo: {
            ...userInfo,
            isAdmin: userInfo.is_admin || false
          }
        })
      }
    } catch (error) {
      console.log('获取用户信息失败:', error)
    }
  },

  // 获取公告列表
  fetchAnnouncements() {
    const app = getApp()
    console.log('[首页] 📡 获取公告数据')
    
    wx.showLoading({
      title: '加载中...',
      mask: true
    })

    wx.request({
      url: `${app.globalData.baseURL}/api/announcements`,
      method: 'GET',
      success: (response) => {
        console.log('[首页] 📊 公告API响应:', response)

        if (response.statusCode === 200 && response.data.code === 0) {
          const announcements = response.data.data.announcements.slice(0, 3) // 只显示前3条
          
          this.setData({
            announcements: announcements,
            loading: false
          })
          
          console.log('[首页] ✅ 公告数据加载完成，共', announcements.length, '条')
          
          // 显示加载完成提示
          wx.showToast({
            title: `📢 加载${announcements.length}条公告`,
            icon: 'none',
            duration: 1500
          })
        } else {
          console.error('[首页] ❌ 公告获取失败:', response.data)
          this.setData({
            announcements: [],
            loading: false
          })
          
          wx.showToast({
            title: '⚠️ 公告加载失败',
            icon: 'none',
            duration: 2000
          })
        }
        
        wx.hideLoading()
      },
      fail: (error) => {
        console.error('[首页] ❌ 公告获取失败:', error)
        this.setData({
          announcements: [],
          loading: false
        })
        
        wx.showToast({
          title: '⚠️ 公告加载失败',
          icon: 'none',
          duration: 2000
        })
        
        wx.hideLoading()
      }
    })
  },

  /**
   * 🌊 启动流式数据推送体验
   */
  startStreamExperience() {
    console.log('[首页] 🚀 启动流式数据推送体验')
    
    // 初始化流式管理器
    const { announcementStream, streamManager } = require('../../utils/stream.js')
    
    this.setData({
      streamConnectTime: new Date()
    })
    
    // 启动公告流式推送
    announcementStream.start((newAnnouncement) => {
      console.log('[首页] 📢 收到流式公告推送:', newAnnouncement.title)
      
      // 🎯 实时体验统计更新
      const currentStats = this.data.experienceStats
      if (newAnnouncement.stream_type === 'realtime_push') {
        this.setData({
          [`experienceStats.realTimePushes`]: currentStats.realTimePushes + 1
        })
      }
      
      // 🚀 动态插入新公告到列表顶部
      const currentNotices = this.data.notices
      const updatedNotices = [newAnnouncement, ...currentNotices.slice(0, 4)] // 保持最多5条
      
      this.setData({
        notices: updatedNotices
      })
      
      // 🎉 新数据推送的视觉反馈
      this.showNewDataFeedback(newAnnouncement)
    })
    
    // 定期更新流式连接状态
    this.streamStatusUpdater = setInterval(() => {
      this.updateStreamStatus()
    }, 2000)
  },

  /**
   * 📊 更新流式连接状态
   */
  updateStreamStatus() {
    const { streamManager, announcementStream } = require('../../utils/stream.js')
    const status = streamManager.getConnectionStatus()
    const announcementStats = announcementStream.getStats()
    
    // 计算连接时长
    const connectTime = this.data.streamConnectTime
    const duration = connectTime ? Math.floor((Date.now() - connectTime.getTime()) / 1000) : 0
    
    this.setData({
      streamStatus: {
        isConnected: status.isConnected,
        connectionTime: status.lastUpdate ? 
          new Date(status.lastUpdate).toLocaleTimeString() : null,
        dataCount: status.dataReceived,
        cacheHitRate: status.cacheHitRate,
        activeStreams: status.activeStreams,
        connectionDuration: duration
      }
    })
    
    // 缓存命中统计
    if (status.cacheHits > this.data.experienceStats.cacheHits) {
      this.setData({
        [`experienceStats.cacheHits`]: status.cacheHits
      })
    }
  },

  /**
   * 🎉 新数据推送的视觉反馈
   */
  showNewDataFeedback(data) {
    // 🎯 差异化反馈：根据数据类型
    if (data.stream_type === 'realtime_push') {
      // 实时推送 - 强反馈
      wx.showToast({
        title: `📢 ${data.title.substring(0, 8)}...`,
        icon: 'none',
        duration: 3000
      })
      
      // 🌊 添加新数据高亮动画效果标记
      const notices = this.data.notices.map((notice, index) => ({
        ...notice,
        isNewPush: index === 0 && notice.id === data.id
      }))
      
      this.setData({ notices })
      
      // 2秒后移除高亮
      setTimeout(() => {
        const updatedNotices = this.data.notices.map(notice => ({
          ...notice,
          isNewPush: false
        }))
        this.setData({ notices: updatedNotices })
      }, 2000)
      
    } else {
      // 初始数据 - 轻反馈
      console.log('[首页] 📥 接收初始公告数据:', data.title)
    }
  },

  /**
   * 🎮 切换演示模式
   */
  toggleDemoMode() {
    const newDemoMode = !this.data.demoMode
    
    this.setData({
      demoMode: newDemoMode
    })
    
    if (newDemoMode) {
      wx.showModal({
        title: '🎮 体验模式',
        content: '演示模式已开启！\n\n您将看到:\n📢 实时公告推送\n📊 流式连接状态\n🎯 性能统计信息\n🌐 网络自适应效果',
        showCancel: false,
        confirmText: '开始体验',
        confirmColor: '#0052d9'
      })
    } else {
      wx.showToast({
        title: '🎮 演示模式已关闭',
        icon: 'none',
        duration: 2000
      })
    }
  },

  /**
   * 🧹 清理缓存体验
   */
  clearCacheExperience() {
    const { streamManager } = require('../../utils/stream.js')
    
    wx.showModal({
      title: '🧹 清理缓存',
      content: '确定要清理所有缓存数据吗？这将重置流式体验统计。',
      confirmText: '清理',
      confirmColor: '#fa5151',
      success: (res) => {
        if (res.confirm) {
          streamManager.clearCache()
          
          // 重置体验统计
          this.setData({
            experienceStats: {
              realTimePushes: 0,
              cacheHits: 0,
              networkAdaptations: 0,
              offlineRecoveries: 0
            }
          })
        }
      }
    })
  },

  /**
   * 📊 查看详细统计
   */
  showDetailedStats() {
    const stats = this.data.streamStatus
    const experience = this.data.experienceStats
    
    const message = `📊 流式连接详情
    
🔗 连接状态: ${stats.isConnected ? '✅ 已连接' : '❌ 未连接'}
⏰ 连接时长: ${stats.connectionDuration || 0} 秒
📡 活跃数据流: ${stats.activeStreams} 个
📥 接收数据量: ${stats.dataCount} 条
💾 缓存命中率: ${stats.cacheHitRate}

🎯 体验统计:
📢 实时推送: ${experience.realTimePushes} 次
📦 缓存命中: ${experience.cacheHits} 次
🌐 网络适应: ${experience.networkAdaptations} 次
📴 离线恢复: ${experience.offlineRecoveries} 次`

    wx.showModal({
      title: '📊 流式体验报告',
      content: message,
      showCancel: false,
      confirmText: '知道了',
      confirmColor: '#0052d9'
    })
  },

  /**
   * 🌐 测试网络适应
   */
  testNetworkAdaptation() {
    wx.showModal({
      title: '🌐 网络适应测试',
      content: '此功能将模拟不同网络环境，测试流式封装的自适应能力。\n\n建议:\n1. 切换到慢速网络\n2. 开启/关闭飞行模式\n3. 观察应用的反应',
      showCancel: false,
      confirmText: '开始测试',
      confirmColor: '#0052d9',
      success: () => {
        // 触发网络检测
        wx.getNetworkType({
          success: (res) => {
            const networkType = res.networkType
            let message = ''
            
            if (networkType === 'none') {
              message = '📴 检测到无网络连接\n已启用离线缓存模式'
              this.setData({
                [`experienceStats.offlineRecoveries`]: this.data.experienceStats.offlineRecoveries + 1
              })
            } else if (['2g', '3g'].includes(networkType)) {
              message = `🐌 检测到慢速网络 (${networkType.toUpperCase()})\n已启用省流模式`
              this.setData({
                [`experienceStats.networkAdaptations`]: this.data.experienceStats.networkAdaptations + 1
              })
            } else {
              message = `📶 网络状况良好 (${networkType.toUpperCase()})\n正常传输模式`
            }
            
            wx.showToast({
              title: message,
              icon: 'none',
              duration: 3000
            })
          }
        })
      }
    })
  },

  // 弹窗确认
  onDialogConfirm() {
    this.setData({ showDialog: false })
    // 跳转到公告详情页
    if (this.data.dialogData.announcement) {
      app.globalData.currentAnnouncement = this.data.dialogData.announcement
      wx.navigateTo({
        url: '/pages/announcement-detail/announcement-detail'
      })
    }
  },

  // 弹窗取消
  onDialogCancel() {
    this.setData({ showDialog: false })
  },

  stopAnnouncementStream() {
    // 实现停止流式推送的逻辑
  },

  // 拨打电话
  makePhoneCall(e) {
    const phone = e.currentTarget.dataset.phone
    const name = e.currentTarget.dataset.name
    
    console.log('[首页] 📞 拨打电话:', name, phone)
    
    wx.makePhoneCall({
      phoneNumber: phone,
      success: () => {
        console.log('[首页] ✅ 拨打成功:', phone)
      },
      fail: (error) => {
        console.error('[首页] ❌ 拨打失败:', error)
        wx.showToast({
          title: '拨打电话失败',
          icon: 'none'
        })
      }
    })
  },

  // 复制电话号码
  copyPhoneNumber(e) {
    const phone = e.currentTarget.dataset.phone
    const name = e.currentTarget.dataset.name
    
    console.log('[首页] 📋 复制电话号码:', name, phone)
    
    wx.setClipboardData({
      data: phone,
      success: () => {
        wx.showToast({
          title: `已复制${name}电话`,
          icon: 'success',
          duration: 2000
        })
      },
      fail: (error) => {
        console.error('[首页] ❌ 复制失败:', error)
        wx.showToast({
          title: '复制失败',
          icon: 'none'
        })
      }
    })
  }
}) 