const app = getApp()
const API = require('../../utils/api.js')

Page({
  data: {
    currentYear: 2024,
    currentMonth: 1,
    calendarVisible: false,
    events: [],
    filteredEvents: [],
    loading: true,
    error: '',
    eventTypes: [
      { value: 'all', text: '全部' },
      { value: 'academic', text: '学术活动' },
      { value: 'social', text: '社团活动' },
      { value: 'sports', text: '体育活动' },
      { value: 'cultural', text: '文化活动' },
      { value: 'competition', text: '比赛活动' }
    ],
    selectedType: 'all',
    selectedTypeText: '全部',
    eventStatuses: ['全部', '即将开始', '进行中', '已结束', '已关注', '未关注', '已报名'],
    selectedStatus: '全部',
    organizers: ['全部', '学术委员会', '学生会', '体育部', '计算机学院', '社团联合会', '教务处'],
    streamStatus: {
      isConnected: false,
      participantUpdates: 0,
      lastUpdate: null
    },
    participantChanges: {},
    showRealTimeUpdates: true,
    autoRefresh: true
  },

  onLoad() {
    console.log('[活动页面] 🎯 页面加载')
    this.setCurrentDate()
    this.loadEvents()
    this.startEventStream()
  },

  setCurrentDate() {
    const now = new Date()
    const currentDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
    this.setData({
      currentDate: currentDate,
      calendarValue: now
    })
  },

  onBack() {
    wx.navigateBack({
      delta: 1
    })
  },

  async loadEvents() {
    console.log('[活动页面] 📥 加载活动数据')
    console.log('[活动页面] 🔍 当前筛选条件:', {
      selectedType: this.data.selectedType,
      selectedStatus: this.data.selectedStatus
    })
    
    this.setData({ loading: true })

    try {
      // 检查token是否存在（不登录也允许浏览）
      const token = wx.getStorageSync('token')
      console.log('[活动页面] 🔑 Token检查:', token ? 'Token存在' : 'Token缺失，但允许浏览')
      
      // 如果选择的是需要登录的筛选项，但没有token，则提示登录
      const selectedStatus = this.data.selectedStatus
      if (!token && (selectedStatus === '已关注' || selectedStatus === '未关注' || selectedStatus === '已报名')) {
        wx.showModal({
          title: '提示',
          content: '查看此类状态需要先登录',
          cancelText: '取消',
          confirmText: '去登录',
          success: (res) => {
            if (res.confirm) {
              wx.navigateTo({
                url: '/pages/login/login'
              })
            } else {
              // 重置为"全部"状态
              this.setData({ selectedStatus: '全部' })
              this.loadEvents()
            }
          }
        })
        this.setData({ loading: false })
        return
      }
      
      // 🔧 使用统一的API模块，根据筛选条件获取活动
      let apiParams = {
        event_type: this.data.selectedType === 'all' ? null : this.data.selectedType
      }
      
      // 处理状态筛选 (复用前面的selectedStatus变量)
      if (selectedStatus !== '全部' && selectedStatus !== '已关注' && selectedStatus !== '未关注' && selectedStatus !== '已报名') {
        // 常规状态筛选
        apiParams.status = selectedStatus
      }
      
      const response = await API.getEvents(apiParams)

      console.log('[活动页面] 📦 API完整响应:', response)

      if (response.code === 0) {
        console.log('[活动页面] ✅ 活动数据加载成功:', response.data.events.length, '条')
        console.log('[活动页面] 📋 原始活动数据:', response.data.events)
        
        let eventsWithProgress = response.data.events.map(event => ({
          ...event,
          id: event.event_id, // 🔧 统一ID字段
          organizer: event.organizer_name, // 🔧 字段映射
          location: event.location_name, // 🔧 字段映射
          participationRate: event.max_participants > 0 ? 
            ((event.current_participants / event.max_participants) * 100).toFixed(1) : '0',
          participationPercent: event.max_participants > 0 ? 
            Math.round((event.current_participants / event.max_participants) * 100) : 0,
          isNearFull: event.max_participants > 0 && 
            (event.current_participants / event.max_participants) > 0.8
        }))
        
        // 🔧 根据关注和报名状态进行筛选 (复用前面的selectedStatus变量)
        if (selectedStatus === '已关注' || selectedStatus === '未关注' || selectedStatus === '已报名') {
          const token = wx.getStorageSync('token')
          if (token) {
            const followedEvents = wx.getStorageSync('followedEvents') || []
            const registeredEvents = wx.getStorageSync('registeredEvents') || []
            
            eventsWithProgress = eventsWithProgress.filter(event => {
              const eventId = event.id
              if (selectedStatus === '已关注') {
                return followedEvents.includes(eventId)
              } else if (selectedStatus === '未关注') {
                return !followedEvents.includes(eventId)
              } else if (selectedStatus === '已报名') {
                return registeredEvents.includes(eventId)
              }
              return true
            })
          } else {
            // 未登录时，这些筛选项返回空结果
            eventsWithProgress = []
          }
        }
        
        this.setData({ 
          events: eventsWithProgress,
          loading: false 
        })
        
        console.log('[活动页面] 🎯 处理后的活动数据:', eventsWithProgress)
        console.log('[活动页面] 📊 setData后的页面状态:', {
          eventsLength: this.data.events.length,
          loading: this.data.loading
        })
        
        if (eventsWithProgress.length === 0) {
          wx.showToast({
            title: '暂无活动数据',
            icon: 'none',
            duration: 2000
          })
        }
      } else {
        console.error('[活动页面] ❌ API返回错误:', response)
        throw new Error(response.message || '活动数据加载失败')
      }
    } catch (error) {
      console.error('[活动页面] ❌ 加载活动失败:', error)
      
      // 检查是否是认证错误
      if (error.message && (error.message.includes('401') || error.message.includes('unauthorized'))) {
        wx.showModal({
          title: '认证失败',
          content: '登录状态已过期，请重新登录',
          showCancel: false,
          confirmText: '去登录',
          success: () => {
            wx.navigateTo({
              url: '/pages/login/login'
            })
          }
        })
      } else {
        wx.showToast({
          title: '❌ 活动加载失败',
          icon: 'none',
          duration: 2000
        })
      }
      
      this.setData({ loading: false })
    }
  },

  /**
   * 🌊 启动活动流式数据更新
   */
  startEventStream() {
    console.log('[活动页面] 🌊 启动活动实时数据流')
    
    try {
      const streamModule = require('../../utils/stream.js')
      const eventStream = streamModule && streamModule.eventStream
      
      if (eventStream && typeof eventStream.start === 'function') {
        eventStream.start((eventData) => {
          console.log('[活动页面] 📊 收到活动更新:', eventData)
          
          this.updateStreamStatus()
          
          if (eventData.update_type === 'participant_change') {
            this.handleParticipantChange(eventData)
            
          } else if (eventData.stream_type === 'initial') {
            this.handleInitialEventData(eventData)
            
          } else {
            this.handleGeneralEventUpdate(eventData)
          }
        })
      } else {
        console.log('[活动页面] ⚠️ 流式更新功能暂不可用，跳过')
        this.setData({
          streamStatus: {
            isConnected: false,
            participantUpdates: 0,
            lastUpdate: null
          }
        })
      }
    } catch (error) {
      console.error('[活动页面] ❌ 启动流式更新失败:', error)
      this.setData({
        streamStatus: {
          isConnected: false,
          participantUpdates: 0,
          lastUpdate: null
        }
      })
    }
    
    this.statusUpdateTimer = setInterval(() => {
      this.updateStreamStatus()
    }, 3000)
  },

  /**
   * 👥 处理参与人数变化
   */
  handleParticipantChange(eventData) {
    const eventId = eventData.id
    const newParticipants = eventData.current_participants
    const maxParticipants = eventData.max_participants
    
    console.log(`[活动页面] 👥 活动 ${eventData.title} 参与人数: ${newParticipants}/${maxParticipants}`)
    
    const currentChanges = this.data.participantChanges
    const changeKey = `event_${eventId}`
    
    if (!currentChanges[changeKey]) {
      currentChanges[changeKey] = {
        count: 0,
        lastChange: Date.now()
      }
    }
    
    currentChanges[changeKey].count++
    currentChanges[changeKey].lastChange = Date.now()
    
    this.setData({
      participantChanges: currentChanges
    })
    
    const updatedEvents = this.data.events.map(event => {
      if (event.id === eventId) {
        const oldParticipants = event.current_participants
        const participationRate = maxParticipants > 0 ? 
          ((newParticipants / maxParticipants) * 100).toFixed(1) : '0'
        
        return {
          ...event,
          current_participants: newParticipants,
          participationRate,
          isNearFull: (newParticipants / maxParticipants) > 0.8,
          hasRecentChange: true,
          participantTrend: newParticipants > oldParticipants ? 'increase' : 
                          newParticipants < oldParticipants ? 'decrease' : 'same'
        }
      }
      return event
    })
    
    this.setData({ 
      events: updatedEvents,
      [`streamStatus.participantUpdates`]: this.data.streamStatus.participantUpdates + 1
    })
    
    this.showParticipantChangeFeedback(eventData, newParticipants - (this.getEventById(eventId)?.current_participants || 0))
    
    setTimeout(() => {
      const resetEvents = this.data.events.map(event => ({
        ...event,
        hasRecentChange: false,
        participantTrend: 'same'
      }))
      this.setData({ events: resetEvents })
    }, 2000)
  },

  /**
   * 📥 处理初始活动数据
   */
  handleInitialEventData(eventData) {
    console.log('[活动页面] 📥 接收初始活动数据:', eventData.title)
    
    // 检查是否是新活动
    const existingEvent = this.data.events.find(event => event.id === eventData.id)
    
    if (!existingEvent) {
      // 新活动，添加到列表
      const newEventWithProgress = {
        ...eventData,
        participationRate: eventData.max_participants > 0 ? 
          ((eventData.current_participants / eventData.max_participants) * 100).toFixed(1) : '0',
        isNearFull: eventData.max_participants > 0 && 
          (eventData.current_participants / eventData.max_participants) > 0.8,
        isNewActivity: true
      }
      
      this.setData({
        events: [newEventWithProgress, ...this.data.events]
      })
      
      // 新活动提示
      wx.showToast({
        title: `🎯 新活动: ${eventData.title}`,
        icon: 'none',
        duration: 3000
      })
      
      // 移除新活动标记
      setTimeout(() => {
        const updatedEvents = this.data.events.map(event => ({
          ...event,
          isNewActivity: false
        }))
        this.setData({ events: updatedEvents })
      }, 3000)
    }
  },

  /**
   * 🎯 处理一般活动更新
   */
  handleGeneralEventUpdate(eventData) {
    console.log('[活动页面] 🎯 活动更新:', eventData.title)
    
    const updatedEvents = this.data.events.map(event => {
      if (event.id === eventData.id) {
        return {
          ...event,
          ...eventData,
          participationRate: eventData.max_participants > 0 ? 
            ((eventData.current_participants / eventData.max_participants) * 100).toFixed(1) : '0',
          isNearFull: eventData.max_participants > 0 && 
            (eventData.current_participants / eventData.max_participants) > 0.8,
          hasUpdate: true
        }
      }
      return event
    })
    
    this.setData({ events: updatedEvents })
    
    setTimeout(() => {
      const resetEvents = this.data.events.map(event => ({
        ...event,
        hasUpdate: false
      }))
      this.setData({ events: resetEvents })
    }, 2000)
  },

  /**
   * 🎉 参与人数变化反馈
   */
  showParticipantChangeFeedback(eventData, change) {
    if (!this.data.showRealTimeUpdates) return
    
    const changeIcon = change > 0 ? '📈' : change < 0 ? '📉' : '➡️'
    const changeText = change > 0 ? `+${change}` : change < 0 ? `${change}` : '无变化'
    
    wx.showToast({
      title: `${changeIcon} ${eventData.title}\n${changeText} 人 (${eventData.current_participants}/${eventData.max_participants})`,
      icon: 'none',
      duration: 2500
    })
    
    // 触觉反馈
    if (Math.abs(change) > 0) {
      wx.vibrateShort({
        type: 'light'
      })
    }
  },

  /**
   * 📊 更新流式状态
   */
  updateStreamStatus() {
    try {
      const streamModule = require('../../utils/stream.js')
      const eventStream = streamModule && streamModule.eventStream
      
      if (eventStream && typeof eventStream.getStats === 'function') {
        const stats = eventStream.getStats()
        
        this.setData({
          streamStatus: {
            isConnected: stats.isConnected || false,
            participantUpdates: stats.participantChanges || 0,
            lastUpdate: stats.lastUpdate ? 
              new Date(stats.lastUpdate).toLocaleTimeString() : null
          }
        })
      } else {
        this.setData({
          streamStatus: {
            isConnected: false,
            participantUpdates: 0,
            lastUpdate: null
          }
        })
      }
    } catch (error) {
      console.error('[活动页面] ❌ 更新流式状态失败:', error)
      this.setData({
        streamStatus: {
          isConnected: false,
          participantUpdates: 0,
          lastUpdate: null
        }
      })
    }
  },

  /**
   * 🛑 停止活动流
   */
  stopEventStream() {
    try {
      const streamModule = require('../../utils/stream.js')
      const eventStream = streamModule && streamModule.eventStream
      
      if (eventStream && typeof eventStream.stop === 'function') {
        eventStream.stop()
      }
    } catch (error) {
      console.error('[活动页面] ❌ 停止流式更新失败:', error)
    }
    
    if (this.statusUpdateTimer) {
      clearInterval(this.statusUpdateTimer)
    }
  },

  /**
   * 🔍 根据ID获取活动
   */
  getEventById(eventId) {
    return this.data.events.find(event => event.id === eventId)
  },

  /**
   * 🎯 查看活动详情
   */
  viewEventDetail(e) {
    const event = e.currentTarget.dataset.event
    
    if (!event) {
      console.error('[活动页面] ❌ 无法获取活动数据')
      wx.showToast({
        title: '获取活动信息失败',
        icon: 'none'
      })
      return
    }
    
    console.log('[活动页面] 🎯 查看活动详情:', event.title)
    
    // 构造完整的活动数据
    const eventDetail = {
      id: event.id || event.event_id,
      title: event.title,
      description: event.description || '这是一个精彩的校园活动，期待您的参与！',
      location: event.location,
      organizer: event.organizer || '学生会',
      status: this.getEventStatus(event),
      startTime: event.start_time || event.event_date,
      endTime: event.end_time,
      date: event.event_date,
      time: event.start_time,
      participants: `${event.current_participants}/${event.max_participants}`,
      agenda: event.agenda || '活动安排详情请关注后续通知',
      requirements: event.requirements || '欢迎所有同学参与，无特殊要求',
      contact: event.contact || '活动负责人：活动组委会',
      reward: event.reward || '参与即可获得活动证书'
    }
    
    // 存储到全局数据
    app.globalData.currentEvent = eventDetail
    
    wx.navigateTo({
      url: '/pages/event-detail/event-detail'
    })
  },

  // 获取活动状态
  getEventStatus(event) {
    const now = new Date()
    const eventDate = new Date(event.event_date)
    
    if (eventDate > now) {
      return 'upcoming'
    } else if (event.current_participants >= event.max_participants) {
      return 'ended'
    } else {
      return 'ongoing'
    }
  },

  /**
   * ✅ 参加活动
   */
  async joinEvent(event) {
    if (event.current_participants >= event.max_participants) {
      wx.showToast({
        title: '😔 活动人数已满',
        icon: 'none',
        duration: 2000
      })
      return
    }
    
    try {
      wx.showLoading({ title: '报名中...' })
      
      // 🔧 使用统一的API模块
      const response = await API.registerEvent(event.event_id || event.id)
      
      if (response.code === 0) {
        wx.hideLoading()
        wx.showToast({
          title: '✅ 参加成功！',
          icon: 'success',
          duration: 2000
        })
        
        // 刷新活动列表
        this.loadEvents()
        
        console.log('[活动页面] ✅ 参加活动成功:', event.title)
      } else {
        throw new Error(response.message || '参加活动失败')
      }
    } catch (error) {
      console.error('[活动页面] ❌ 参加活动失败:', error)
      wx.hideLoading()
      wx.showToast({
        title: '参加失败，请重试',
        icon: 'none',
        duration: 2000
      })
    }
  },

  /**
   * 🔄 手动刷新
   */
  onRefresh() {
    console.log('[活动页面] 🔄 手动刷新')
    this.loadEvents()
    
    wx.showToast({
      title: '🔄 刷新中...',
      icon: 'none',
      duration: 1000
    })
  },

  /**
   * 🎮 切换实时更新显示
   */
  toggleRealTimeUpdates() {
    const newState = !this.data.showRealTimeUpdates
    
    this.setData({
      showRealTimeUpdates: newState
    })
    
    wx.showToast({
      title: newState ? '🌊 已开启实时更新' : '🔇 已关闭实时更新',
      icon: 'none',
      duration: 2000
    })
  },

  /**
   * 📊 查看参与统计
   */
  showParticipantStats() {
    const stats = this.data.streamStatus
    const changes = this.data.participantChanges
    
    let changesText = '📊 参与人数变化记录:\n\n'
    
    if (Object.keys(changes).length === 0) {
      changesText += '暂无变化记录'
    } else {
      Object.entries(changes).forEach(([key, value]) => {
        const eventId = key.replace('event_', '')
        const event = this.getEventById(parseInt(eventId))
        if (event) {
          changesText += `🎯 ${event.title}: ${value.count} 次变化\n`
        }
      })
    }
    
    const message = `🌊 实时数据统计

🔗 连接状态: ${stats.isConnected ? '✅ 已连接' : '❌ 未连接'}
📊 参与人数更新: ${stats.participantUpdates} 次
⏰ 最后更新: ${stats.lastUpdate || '无'}

${changesText}`

    wx.showModal({
      title: '📊 实时统计',
      content: message,
      showCancel: false,
      confirmText: '知道了',
      confirmColor: '#0052d9'
    })
  },

  onUnload() {
    console.log('[活动页面] 👋 页面卸载，停止活动流')
    this.stopEventStream()
  },

  onShow() {
    console.log('[活动页面] 👀 页面显示')
    this.updateStreamStatus()
  },

  onHide() {
    console.log('[活动页面] 页面隐藏')
    // 停止流式更新以节省资源
    this.stopEventStream()
  },

  onPullDownRefresh() {
    console.log('[活动页面] 下拉刷新')
    this.loadEvents().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onTypeChange(e) {
    const typeIndex = e.detail.value
    const selectedTypeData = this.data.eventTypes[typeIndex]
    const selectedType = selectedTypeData.value
    const selectedTypeText = selectedTypeData.text
    console.log('[活动页面] 类型筛选:', selectedType, selectedTypeText)
    this.setData({ 
      selectedType: selectedType,
      selectedTypeText: selectedTypeText
    })
    this.loadEvents()
  },

  onStatusChange(e) {
    const statusIndex = e.detail.value
    const selectedStatus = this.data.eventStatuses[statusIndex]
    console.log('[活动页面] 状态筛选:', selectedStatus)
    this.setData({ selectedStatus: selectedStatus })
    this.loadEvents()
  },

  onDateSelect(e) {
    const selectedDate = e.detail.value
    console.log('[活动页面] 选择日期:', selectedDate)
    
    this.setData({
      currentDate: selectedDate,
      calendarVisible: false
    })
    
    // TODO: 根据选择的日期筛选活动
  },

  onCalendarClose() {
    this.setData({
      calendarVisible: false
    })
  },

  /**
   * 🔗 测试流式连接状态
   */
  testStreamConnection() {
    const status = this.data.streamStatus
    
    wx.showModal({
      title: '🌊 活动流式状态',
      content: `连接状态：${status.isConnected ? '✅ 已连接' : '❌ 未连接'}\n活跃流数量：${status.activeStreams}\n最后更新：${status.lastUpdate || '无'}\n更新次数：${status.updateCount}`,
      showCancel: false,
      confirmText: '确定',
      confirmColor: '#0052d9'
    })
  },

  getEventTypeText(type) {
    const typeMap = {
      'academic': '学术活动',
      'social': '社团活动',
      'sports': '体育活动',
      'cultural': '文化活动',
      'competition': '比赛活动'
    }
    return typeMap[type] || '其他活动'
  },

  getStatusText(status) {
    const statusMap = {
      'upcoming': '即将开始',
      'ongoing': '进行中',
      'completed': '已结束',
      'cancelled': '已取消'
    }
    return statusMap[status] || '未知'
  },

  getStatusColor(status) {
    const colorMap = {
      'upcoming': '#0052d9',
      'ongoing': '#00a870',
      'completed': '#909399',
      'cancelled': '#e34d59'
    }
    return colorMap[status] || '#909399'
  }
}) 