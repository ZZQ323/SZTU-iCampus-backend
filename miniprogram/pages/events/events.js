const app = getApp()
const { eventStream, streamManager } = require('../../utils/stream.js')

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
    eventStatuses: ['全部', '即将开始', '进行中', '已结束'],
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
    this.setData({ loading: true })

    try {
      const baseURL = getApp().globalData.baseURL
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${baseURL}/api/events`,
          method: 'GET',
          success: resolve,
          fail: reject
        })
      })

      if (response.statusCode === 200 && response.data.success) {
        console.log('[活动页面] ✅ 活动数据加载成功:', response.data.data.length, '条')
        
        const eventsWithProgress = response.data.data.map(event => ({
          ...event,
          participationRate: event.max_participants > 0 ? 
            ((event.current_participants / event.max_participants) * 100).toFixed(1) : '0',
          isNearFull: event.max_participants > 0 && 
            (event.current_participants / event.max_participants) > 0.8
        }))
        
        this.setData({ 
          events: eventsWithProgress,
          loading: false 
        })
      } else {
        throw new Error('活动数据加载失败')
      }
    } catch (error) {
      console.error('[活动页面] ❌ 加载活动失败:', error)
      
      wx.showToast({
        title: '❌ 活动加载失败',
        icon: 'none',
        duration: 2000
      })
      
      this.setData({ loading: false })
    }
  },

  /**
   * 🌊 启动活动流式数据更新
   */
  startEventStream() {
    console.log('[活动页面] 🌊 启动活动实时数据流')
    
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
    const { eventStream } = require('../../utils/stream.js')
    const stats = eventStream.getStats()
    
    this.setData({
      streamStatus: {
        isConnected: stats.isConnected,
        participantUpdates: stats.participantChanges || 0,
        lastUpdate: stats.lastUpdate ? 
          new Date(stats.lastUpdate).toLocaleTimeString() : null
      }
    })
  },

  /**
   * 🛑 停止活动流
   */
  stopEventStream() {
    const { eventStream } = require('../../utils/stream.js')
    eventStream.stop()
    
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
    console.log('[活动页面] 🎯 查看活动详情:', event.title)
    
    // 构造完整的活动数据
    const eventDetail = {
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
  joinEvent(event) {
    if (event.current_participants >= event.max_participants) {
      wx.showToast({
        title: '😔 活动人数已满',
        icon: 'none',
        duration: 2000
      })
      return
    }
    
    wx.showToast({
      title: '✅ 参加成功！',
      icon: 'success',
      duration: 2000
    })
    
    // 模拟参与成功，触发参与人数增加
    // 在实际应用中，这里应该调用后端API
    console.log('[活动页面] ✅ 模拟参加活动:', event.title)
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
    const typeFilter = e.detail.value
    console.log('[活动页面] 类型筛选:', typeFilter)
    this.setData({ selectedType: typeFilter })
    this.loadEvents()
  },

  onStatusChange(e) {
    const statusFilter = e.detail.value
    console.log('[活动页面] 状态筛选:', statusFilter)
    this.setData({ selectedStatus: statusFilter })
    this.loadEvents()
  },

  viewEvent(e) {
    const event = e.currentTarget.dataset.event
    console.log('[活动页面] 查看活动详情:', event.title)
    
    const participantProgress = event.max_participants > 0 ? 
      Math.round((event.current_participants / event.max_participants) * 100) : 0
    
    wx.showModal({
      title: event.title,
      content: `📍 地点：${event.location}\n⏰ 时间：${event.start_time}\n👥 参与人数：${event.current_participants}/${event.max_participants} (${participantProgress}%)\n📝 描述：${event.description}\n\n主办方：${event.organizer}`,
      showCancel: true,
      cancelText: '关闭',
      confirmText: '我要参加',
      confirmColor: '#0052d9',
      success: (res) => {
        if (res.confirm) {
          this.joinEvent(event)
        }
      }
    })
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