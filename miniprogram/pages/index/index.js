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
      { title: '通知', icon: '📋', path: '/pages/notices/notices' },
      { title: '活动', icon: '🎯', path: '/pages/events/events' },
      { title: '成绩', icon: '📊', path: '/pages/grades/grades' },
      { title: '考试', icon: '📝', path: '/pages/exams/exams' },
      { title: '校园卡', icon: '💳', path: '/pages/campus-card/campus-card' },
      { title: '图书馆', icon: '📚', path: '/pages/library/library' }
    ],
    loading: true,
    streamStatus: {
      isConnected: false,
      activeStreams: 0,
      lastUpdate: null
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
    streamConnectTime: null
  },

  onLoad() {
    console.log('[首页] 🏠 页面加载')
    this.getUserInfo()
    this.fetchAnnouncements()
    this.startStreamExperience()
  },

  async getUserInfo() {
    // 模拟用户信息
    this.setData({
      userInfo: {
        name: '同学',
        studentId: '2024001',
        college: '计算机与软件学院'
      }
    })
  },

  async fetchAnnouncements() {
    const app = getApp()
    console.log('[首页] 📡 获取公告数据')
    
    try {
      wx.showLoading({
        title: '加载中...',
        mask: true
      })

      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/announcements`,
          method: 'GET',
          success: resolve,
          fail: reject
        })
      })

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
        throw new Error(response.data.message || '获取公告失败')
      }
    } catch (error) {
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
    } finally {
      wx.hideLoading()
    }
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
        lastUpdate: status.lastUpdate ? 
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

  onShow() {
    console.log('[首页] 👀 页面显示')
    // 页面重新显示时更新状态
    this.updateStreamStatus()
  },

  onHide() {
    console.log('[首页] 页面隐藏')
    // 停止流式推送以节省资源
    this.stopAnnouncementStream()
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
    this.fetchAnnouncements().then(() => {
      wx.stopPullDownRefresh()
      this.clearNewAnnouncementCount()
    })
  },

  // 导航方法
  navigateToAnnouncements() {
    this.clearNewAnnouncementCount()
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
    const announcement = e.currentTarget.dataset.announcement
    console.log('[首页] 查看公告详情:', announcement.title)
    
    wx.showModal({
      title: announcement.title,
      content: `${announcement.content}\n\n发布部门：${announcement.department}\n发布时间：${announcement.date} ${announcement.time}`,
      showCancel: false,
      confirmText: '知道了',
      confirmColor: '#0052d9'
    })
  },

  /**
   * 🔗 测试流式连接状态
   */
  testStreamConnection() {
    const status = this.data.streamStatus
    
    wx.showModal({
      title: '🌊 流式连接状态',
      content: `连接状态：${status.isConnected ? '✅ 已连接' : '❌ 未连接'}\n活跃流数量：${status.activeStreams}\n最后更新：${status.lastUpdate || '无'}`,
      showCancel: false,
      confirmText: '确定',
      confirmColor: '#0052d9'
    })
  },

  onBack() {
    // 首页通常不需要返回按钮
  }
}) 