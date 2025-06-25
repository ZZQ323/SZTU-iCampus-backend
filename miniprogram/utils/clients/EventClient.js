const ResourceClient = require('../ResourceClient')
const DataProcessor = require('../DataProcessor')

/**
 * 活动客户端
 * 处理活动相关的API操作
 * 包括活动列表、报名、关注、状态更新等
 */
class EventClient extends ResourceClient {
  constructor() {
    super('http://localhost:8000', 'events')
    this.cacheTimeout = 3 * 60 * 1000 // 3分钟缓存，活动数据更新较频繁
  }

  /**
   * 获取活动列表
   * @param {Object} params 查询参数
   * @param {boolean} useCache 是否使用缓存
   * @returns {Promise<Array>} 活动列表
   */
  async getEvents(params = {}, useCache = true) {
    const cacheKey = `events_${JSON.stringify(params)}`
    
    if (useCache) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        console.log('[EventClient] 📦 使用缓存的活动数据')
        return cached
      }
    }

    try {
      const response = await this.request('/events', {
        method: 'GET',
        data: params
      })
      
      const processedEvents = this.processEventList(response)
      
      // 设置缓存
      this.setCache(cacheKey, processedEvents, this.cacheTimeout)
      
      return processedEvents
    } catch (error) {
      console.error('[EventClient] 获取活动列表失败:', error)
      throw error
    }
  }

  /**
   * 获取活动详情
   * @param {string|number} eventId 活动ID
   * @returns {Promise<Object>} 活动详情
   */
  async getEventDetail(eventId) {
    const cacheKey = `event_detail_${eventId}`
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request(`/events/${eventId}`, {
        method: 'GET'
      })
      
      const processedDetail = this.processEventDetail(response)
      
      // 详情缓存时间较长
      this.setCache(cacheKey, processedDetail, 10 * 60 * 1000)
      
      return processedDetail
    } catch (error) {
      console.error('[EventClient] 获取活动详情失败:', error)
      throw error
    }
  }

  /**
   * 报名参加活动
   * @param {string|number} eventId 活动ID
   * @returns {Promise<Object>} 报名结果
   */
  async joinEvent(eventId) {
    try {
      const response = await this.request(`/events/${eventId}/join`, {
        method: 'POST'
      })
      
      // 清除相关缓存
      this.clearEventCache(eventId)
      
      return {
        success: true,
        message: '报名成功',
        data: response
      }
    } catch (error) {
      console.error('[EventClient] 报名活动失败:', error)
      throw error
    }
  }

  /**
   * 取消报名
   * @param {string|number} eventId 活动ID
   * @returns {Promise<Object>} 取消结果
   */
  async cancelJoin(eventId) {
    try {
      const response = await this.request(`/events/${eventId}/cancel`, {
        method: 'POST'
      })
      
      // 清除相关缓存
      this.clearEventCache(eventId)
      
      return {
        success: true,
        message: '取消报名成功',
        data: response
      }
    } catch (error) {
      console.error('[EventClient] 取消报名失败:', error)
      throw error
    }
  }

  /**
   * 关注活动
   * @param {string|number} eventId 活动ID
   * @returns {Promise<Object>} 关注结果
   */
  async followEvent(eventId) {
    try {
      const response = await this.request(`/events/${eventId}/follow`, {
        method: 'POST'
      })
      
      return {
        success: true,
        message: '关注成功',
        data: response
      }
    } catch (error) {
      console.error('[EventClient] 关注活动失败:', error)
      throw error
    }
  }

  /**
   * 取消关注
   * @param {string|number} eventId 活动ID
   * @returns {Promise<Object>} 取消关注结果
   */
  async unfollowEvent(eventId) {
    try {
      const response = await this.request(`/events/${eventId}/unfollow`, {
        method: 'POST'
      })
      
      return {
        success: true,
        message: '取消关注成功',
        data: response
      }
    } catch (error) {
      console.error('[EventClient] 取消关注失败:', error)
      throw error
    }
  }

  /**
   * 获取我的活动
   * @param {string} type 活动类型：joined|followed|created
   * @returns {Promise<Array>} 我的活动列表
   */
  async getMyEvents(type = 'joined') {
    try {
      const response = await this.request('/events/my', {
        method: 'GET',
        data: { type }
      })
      
      return this.processEventList(response)
    } catch (error) {
      console.error('[EventClient] 获取我的活动失败:', error)
      throw error
    }
  }

  /**
   * 搜索活动
   * @param {string} keyword 搜索关键词
   * @param {Object} filters 过滤条件
   * @returns {Promise<Array>} 搜索结果
   */
  async searchEvents(keyword, filters = {}) {
    try {
      const params = {
        search: keyword,
        keyword: keyword,
        ...filters
      }
      
      const response = await this.request('/events/search', {
        method: 'GET',
        data: params
      })
      
      return this.processEventList(response)
    } catch (error) {
      console.error('[EventClient] 搜索活动失败:', error)
      throw error
    }
  }

  /**
   * 获取活动统计
   * @returns {Promise<Object>} 活动统计信息
   */
  async getEventStatistics() {
    const cacheKey = 'event_statistics'
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request('/events/statistics', {
        method: 'GET'
      })
      
      const processedStats = this.processEventStatistics(response)
      
      // 统计信息缓存时间较长
      this.setCache(cacheKey, processedStats, 30 * 60 * 1000)
      
      return processedStats
    } catch (error) {
      console.error('[EventClient] 获取活动统计失败:', error)
      return this.getDefaultStatistics()
    }
  }

  /**
   * 处理活动列表数据
   * @param {Array|Object} data 原始活动数据
   * @returns {Array} 处理后的活动列表
   */
  processEventList(data) {
    let events = []
    
    if (Array.isArray(data)) {
      events = data
    } else if (data && data.events) {
      events = data.events
    } else if (data && data.list) {
      events = data.list
    } else {
      return []
    }

    return events.map(event => this.processEventItem(event))
  }

  /**
   * 处理单个活动数据
   * @param {Object} event 原始活动数据
   * @returns {Object} 处理后的活动数据
   */
  processEventItem(event) {
    if (!event || typeof event !== 'object') {
      return event
    }

    const participationRate = event.max_participants > 0 
      ? ((event.current_participants / event.max_participants) * 100).toFixed(1)
      : '0'

    return {
      id: event.event_id || event.id,
      title: event.title || event.event_name,
      description: event.description || '',
      organizer: event.organizer_name || event.organizer,
      location: event.location_name || event.location,
      startTime: DataProcessor.formatDate(event.start_time, 'YYYY-MM-DD HH:mm'),
      endTime: DataProcessor.formatDate(event.end_time, 'YYYY-MM-DD HH:mm'),
      relativeStartTime: DataProcessor.formatRelativeTime(event.start_time),
      eventType: event.event_type || 'other',
      status: this.getEventStatus(event),
      maxParticipants: event.max_participants || 0,
      currentParticipants: event.current_participants || 0,
      participationRate: participationRate,
      participationPercent: Math.round(parseFloat(participationRate)),
      isNearFull: parseFloat(participationRate) > 80,
      
      // 状态标识
      isJoined: event.is_joined || false,
      isFollowed: event.is_followed || false,
      canJoin: this.canJoinEvent(event),
      
      // 其他信息
      category: event.category || 'other',
      tags: event.tags || [],
      images: event.images || [],
      registrationDeadline: event.registration_deadline 
        ? DataProcessor.formatDate(event.registration_deadline, 'YYYY-MM-DD HH:mm')
        : null,
      
      // 原始数据
      raw: event
    }
  }

  /**
   * 处理活动详情数据
   * @param {Object} data 原始活动详情
   * @returns {Object} 处理后的活动详情
   */
  processEventDetail(data) {
    const processedEvent = this.processEventItem(data)
    
    // 详情页面需要更多信息
    return {
      ...processedEvent,
      fullDescription: data.full_description || data.description || '',
      requirements: data.requirements || '',
      contact: data.contact || {},
      schedule: data.schedule || [],
      participants: (data.participants || []).map(participant => ({
        id: participant.user_id,
        name: participant.name,
        avatar: participant.avatar,
        joinTime: DataProcessor.formatDate(participant.join_time, 'YYYY-MM-DD HH:mm')
      })),
      comments: (data.comments || []).map(comment => ({
        id: comment.id,
        user: comment.user_name,
        content: comment.content,
        createTime: DataProcessor.formatRelativeTime(comment.created_at)
      })),
      relatedEvents: (data.related_events || []).map(event => this.processEventItem(event))
    }
  }

  /**
   * 处理活动统计数据
   * @param {Object} data 原始统计数据
   * @returns {Object} 处理后的统计数据
   */
  processEventStatistics(data) {
    return {
      totalEvents: data.total_events || 0,
      activeEvents: data.active_events || 0,
      completedEvents: data.completed_events || 0,
      myJoinedEvents: data.my_joined_events || 0,
      myFollowedEvents: data.my_followed_events || 0,
      
      // 类型分布
      typeDistribution: data.type_distribution || {},
      
      // 参与度统计
      participationStats: {
        averageParticipation: data.average_participation || 0,
        highParticipationEvents: data.high_participation_events || 0,
        totalParticipants: data.total_participants || 0
      },
      
      // 热门活动
      popularEvents: (data.popular_events || []).map(event => this.processEventItem(event))
    }
  }

  /**
   * 获取活动状态
   * @param {Object} event 活动数据
   * @returns {string} 活动状态
   */
  getEventStatus(event) {
    const now = new Date()
    const startTime = new Date(event.start_time)
    const endTime = new Date(event.end_time)
    
    if (now < startTime) {
      return 'upcoming'
    } else if (now >= startTime && now <= endTime) {
      return 'ongoing'
    } else {
      return 'completed'
    }
  }

  /**
   * 判断是否可以报名
   * @param {Object} event 活动数据
   * @returns {boolean} 是否可以报名
   */
  canJoinEvent(event) {
    const now = new Date()
    const startTime = new Date(event.start_time)
    const registrationDeadline = event.registration_deadline 
      ? new Date(event.registration_deadline)
      : startTime
    
    // 检查是否已满员
    if (event.max_participants > 0 && event.current_participants >= event.max_participants) {
      return false
    }
    
    // 检查是否已过报名截止时间
    if (now > registrationDeadline) {
      return false
    }
    
    // 检查是否已报名
    if (event.is_joined) {
      return false
    }
    
    return true
  }

  /**
   * 清除活动相关缓存
   * @param {string|number} eventId 活动ID
   */
  clearEventCache(eventId) {
    this.clearCache(`event_detail_${eventId}`)
    
    // 清除列表缓存
    const { keys } = wx.getStorageInfoSync()
    const eventCacheKeys = keys.filter(key => key.includes('events_'))
    
    eventCacheKeys.forEach(key => {
      wx.removeStorageSync(key)
    })
  }

  /**
   * 获取默认统计信息
   * @returns {Object} 默认统计
   */
  getDefaultStatistics() {
    return {
      totalEvents: 0,
      activeEvents: 0,
      completedEvents: 0,
      myJoinedEvents: 0,
      myFollowedEvents: 0,
      typeDistribution: {},
      participationStats: {
        averageParticipation: 0,
        highParticipationEvents: 0,
        totalParticipants: 0
      },
      popularEvents: []
    }
  }

  /**
   * 错误处理
   * @param {Error} error 错误对象
   * @param {string} url 请求URL
   */
  handleError(error, url) {
    console.error(`[EventClient] ❌ 请求失败:`, url, error.message)
    
    if (error.message.includes('401')) {
      throw new Error('登录已过期，请重新登录后查看活动')
    } else if (error.message.includes('403')) {
      throw new Error('暂无权限访问此活动')
    } else if (error.message.includes('网络')) {
      throw new Error('网络连接失败，请检查网络设置')
    } else {
      throw error
    }
  }
}

module.exports = EventClient 