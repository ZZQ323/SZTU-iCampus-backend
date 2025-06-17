/**
 * SZTU iCampus 流式数据管理器 - 企业级解决方案
 * 核心优势：智能缓存 + 增量更新 + 优雅降级 + 用户感知优化
 */

class StreamManager {
  constructor() {
    this.streams = new Map()
      // 每个流有唯一的 streamId 作为键。
    this.eventBus = new Map()
      // 管理和触发事件回调
    this.isConnected = false
      // 是否有活跃的连接
    this.reconnectAttempts = 0
      // 当前已经尝试了的重连次数
    this.maxReconnectAttempts = 5
      // 最大重连尝试次数
    this.reconnectDelay = 1000
      // 重连延时，每次重连会增加等待时间。

    // 流式数据缓存，使用 Map 存储数据，并进行过期管理
    this.dataCache = new Map()
    // 缓存过期时间（5分钟），缓存超过此时间会被清理。
    this.cacheExpiry = 5 * 60 * 1000 // 5分钟缓存

    // 性能统计
    this.stats = {
      cacheHits: 0, // 记录缓存命中
      cacheMisses: 0, // 缓存未命中
      streamConnections: 0, // 连接次数
      dataReceived: 0, // 接收的数据量
      lastUpdate: null // 上次更新的ID？
    }
  }

  /**
   *  智能连接流式数据源
   */
  connect(streamId, url, onData, onError) {
    /**
     * 连接到指定流数据源。如果流已存在，先断开旧的连接
     */
    if (this.streams.has(streamId)) {
      console.log(`[StreamManager]  流 ${streamId} 已存在，先断开旧连接`)
      this.disconnect(streamId)
    }

    console.log(`[StreamManager] 🌊 连接流式数据源: ${streamId}`)
    console.log(`[StreamManager] 📡 数据源地址: ${url}`)

    // 优雅降级：网络检查
    this.checkNetworkAndConnect(streamId, url, onData, onError)
  }

  /**
   * 网络状态检查与优雅降级
    * 检查网络类型，若无网络则启用离线模式；
    * 若网络为慢速（2G/3G），则启用省流模式；
    * 否则，尝试建立连接
   */
  checkNetworkAndConnect(streamId, url, onData, onError) {
    const networkType = wx.getNetworkType()

    networkType.then(res => {
      console.log(`[StreamManager] 📶 网络类型: ${res.networkType}`)

      if (res.networkType === 'none') {
        console.log(`[StreamManager] ⚠️ 无网络连接，启用离线模式`)
        this.handleOfflineMode(streamId, onData)
        return
      }

      // 根据网络类型调整策略
      const isSlowNetwork = ['2g', '3g'].includes(res.networkType)
      if (isSlowNetwork) {
        console.log(`[StreamManager] 🐌 检测到慢速网络，优化传输策略`)
        wx.showToast({
          title: '📶 网络较慢，已启用省流模式',
          icon: 'none',
          duration: 2000
        })
      }

      this.establishConnection(streamId, url, onData, onError, isSlowNetwork)
    })
  }

  /**
   *  建立实际连接
   */
  establishConnection(streamId, url, onData, onError, isSlowNetwork = false) {
    const requestTask = wx.request({
      url: url,
      method: 'GET',
      enableChunked: true,
      responseType: 'text',
      timeout: isSlowNetwork ? 30000 : 15000, // 慢网络延长超时
      success: (res) => {
        console.log(`[StreamManager] ✅ 流 ${streamId} 连接成功`)
        this.isConnected = true
        this.reconnectAttempts = 0
        this.stats.streamConnections++

        // 用户体验：连接成功提示
        wx.showToast({
          title: '🌊 实时数据已连接',
          icon: 'none',
          duration: 1500
        })

        // 轻微震动反馈
        wx.vibrateShort({
          type: 'light'
        })
      },
      fail: (err) => {
        console.error(`[StreamManager] ❌ 流 ${streamId} 连接失败:`, err)
        this.isConnected = false

        // 🔄 智能重连策略
        if (onError) onError(err)
        this.handleConnectionFailure(streamId, url, onData, onError, isSlowNetwork)
      }
    })

    // 数据接收处理
    requestTask.onChunkReceived((res) => {
      const decoder = new TextDecoder()
      const chunk = decoder.decode(res.data)

      if (chunk.trim()) {
        console.log(`[StreamManager] 📥 收到 ${streamId} 数据块`)
        this.stats.dataReceived++
        this.stats.lastUpdate = new Date()

        this.processStreamData(chunk, onData, streamId)
      }
    })

    this.streams.set(streamId, requestTask)
    return requestTask
  }

  /**
   *  智能数据处理 + 缓存策略
   */
  processStreamData(streamData, onData, streamId) {
    try {
      const lines = streamData.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonData = line.substring(6).trim()
          if (jsonData) {
            try {
              const data = JSON.parse(jsonData)
              console.log(`[StreamManager] 🔄 处理 ${streamId} 数据:`, data.title || data.type || 'unknown')

              // 🚀 智能缓存：缓存重要数据
              if (data.id && (data.title || data.course_name)) {
                this.cacheData(streamId, data.id, data)
              }

              // 🎯 用户体验：不同类型数据的差异化反馈
              this.provideUserFeedback(data, streamId)

              if (onData) onData(data)

            } catch (parseError) {
              console.warn(`[StreamManager] ⚠️ JSON解析错误:`, parseError)
            }
          }
        }
      }
    } catch (error) {
      console.error(`[StreamManager] ❌ 数据处理错误:`, error)
    }
  }

  /**
   *  差异化用户反馈
   */
  provideUserFeedback(data, streamId) {
    // 不同类型数据的差异化体验
    if (data.stream_type === 'realtime_push') {
      // 实时推送数据 - 强烈反馈
      wx.vibrateShort({ type: 'heavy' })

    } else if (data.update_type === 'participant_change') {
      // 参与人数变化 - 轻微反馈
      wx.vibrateShort({ type: 'light' })

    } else if (data.type === 'push_success') {
      // 推送成功反馈 - 无震动，仅日志
      console.log(`[StreamManager] ✅ ${data.message}`)
    }
  }

  /**
   *  智能数据缓存
   */
  cacheData(streamId, dataId, data) {
    const cacheKey = `${streamId}_${dataId}`
    const cacheEntry = {
      data: data,
      timestamp: Date.now(),
      accessCount: 1
    }

    // 检查是否已缓存
    if (this.dataCache.has(cacheKey)) {
      this.stats.cacheHits++
      // 更新访问次数
      const existing = this.dataCache.get(cacheKey)
      existing.accessCount++
      existing.timestamp = Date.now() // 刷新缓存时间
    } else {
      this.stats.cacheMisses++
      this.dataCache.set(cacheKey, cacheEntry)
    }

    // 🧹 缓存清理：定期清理过期缓存
    this.cleanupExpiredCache()
  }

  /**
   *  缓存清理机制
   */
  cleanupExpiredCache() {
    const now = Date.now()
    let cleanedCount = 0

    for (const [key, entry] of this.dataCache.entries()) {
      if (now - entry.timestamp > this.cacheExpiry) {
        this.dataCache.delete(key)
        cleanedCount++
      }
    }

    if (cleanedCount > 0) {
      console.log(`[StreamManager] 🧹 清理了 ${cleanedCount} 个过期缓存`)
    }
  }

  /**
   *  离线模式处理
   */
  handleOfflineMode(streamId, onData) {
    console.log(`[StreamManager] 📴 进入离线模式`)

    // 用户体验：离线提示
    wx.showModal({
      title: '📴 网络连接中断',
      content: '当前无网络连接，将为您提供缓存数据。网络恢复后将自动重新连接实时数据。',
      showCancel: false,
      confirmText: '知道了',
      confirmColor: '#0052d9'
    })

    // 智能降级：提供缓存数据
    const cachedData = this.getCachedDataForStream(streamId)
    if (cachedData.length > 0) {
      console.log(`[StreamManager] 📦 提供 ${cachedData.length} 条缓存数据`)

      cachedData.forEach((data, index) => {
        setTimeout(() => {
          const offlineData = {
            ...data,
            isOfflineData: true,
            cacheTime: new Date(Date.now() - Math.random() * 3600000).toISOString()
          }
          if (onData) onData(offlineData)
        }, index * 100) // 模拟流式传输
      })

      wx.showToast({
        title: `📦 已加载${cachedData.length}条缓存数据`,
        icon: 'none',
        duration: 2000
      })
    }
  }

  /**
   * 获取指定流的缓存数据
   */
  getCachedDataForStream(streamId) {
    const cachedData = []
    const prefix = `${streamId}_`

    for (const [key, entry] of this.dataCache.entries()) {
      if (key.startsWith(prefix)) {
        cachedData.push(entry.data)
      }
    }

    // 按时间倒序排列
    return cachedData.sort((a, b) =>
      new Date(b.created_at || b.timestamp) - new Date(a.created_at || a.timestamp)
    )
  }

  /**
   *  连接失败处理
   */
  handleConnectionFailure(streamId, url, onData, onError, isSlowNetwork) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

      console.log(`[StreamManager] 🔄 ${delay}ms后尝试重连 ${streamId} (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

      // 🎯 用户体验：重连进度提示
      wx.showToast({
        title: `🔄 重连中... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`,
        icon: 'none',
        duration: delay
      })

      setTimeout(() => {
        this.establishConnection(streamId, url, onData, onError, isSlowNetwork)
      }, delay)
    } else {
      console.error(`[StreamManager] ❌ 流 ${streamId} 重连失败，启用离线模式`)

      wx.showModal({
        title: '⚠️ 连接失败',
        content: '实时数据连接失败，已切换至离线模式。您可以继续浏览缓存数据。',
        showCancel: true,
        cancelText: '继续离线',
        confirmText: '重试连接',
        confirmColor: '#0052d9',
        success: (res) => {
          if (res.confirm) {
            // 重置重连计数，重新尝试
            this.reconnectAttempts = 0
            this.checkNetworkAndConnect(streamId, url, onData, onError)
          } else {
            // 进入离线模式
            this.handleOfflineMode(streamId, onData)
          }
        }
      })
    }
  }

  /**
   *  断开流连接
   */
  disconnect(streamId) {
    const stream = this.streams.get(streamId)
    if (stream) {
      stream.abort()
      this.streams.delete(streamId)
      console.log(`[StreamManager] 🔌 已断开流: ${streamId}`)
    }
  }

  /**
   * 🚫 断开所有流连接
   */
  disconnectAll() {
    console.log(`[StreamManager] 🚫 断开所有流连接`)
    for (const [streamId, stream] of this.streams) {
      stream.abort()
    }
    this.streams.clear()
    this.isConnected = false
  }

  /**
   * 📡 事件总线
   */
  on(event, callback) {
    if (!this.eventBus.has(event)) {
      this.eventBus.set(event, [])
    }
    this.eventBus.get(event).push(callback)
  }

  emit(event, data) {
    const callbacks = this.eventBus.get(event)
    if (callbacks) {
      callbacks.forEach(callback => callback(data))
    }
  }

  off(event, callback) {
    const callbacks = this.eventBus.get(event)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * 📊 获取性能统计
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      activeStreams: this.streams.size,
      reconnectAttempts: this.reconnectAttempts,
      cacheSize: this.dataCache.size,
      cacheHitRate: this.stats.cacheHits + this.stats.cacheMisses > 0 ?
        (this.stats.cacheHits / (this.stats.cacheHits + this.stats.cacheMisses) * 100).toFixed(1) + '%' : '0%',
      totalConnections: this.stats.streamConnections,
      dataReceived: this.stats.dataReceived,
      lastUpdate: this.stats.lastUpdate
    }
  }

  /**
   * 🧹 清理所有缓存
   */
  clearCache() {
    const size = this.dataCache.size
    this.dataCache.clear()
    console.log(`[StreamManager] 🧹 清理了所有缓存 (${size} 条)`)

    wx.showToast({
      title: `🧹 清理了${size}条缓存`,
      icon: 'none',
      duration: 1500
    })
  }
}

/**
 * 📢 公告流式数据管理 - 优化版
 */
class AnnouncementStream {
  constructor() {
    this.streamManager = new StreamManager()
    this.isActive = false
    this.lastAnnouncementId = 0
  }

  start(onNewAnnouncement) {
    if (this.isActive) {
      console.log('[AnnouncementStream] 📢 公告流已激活')
      return
    }

    console.log('[AnnouncementStream] 🚀 启动公告实时推送')
    const baseUrl = getApp().globalData.baseUrl

    this.streamManager.connect(
      'announcements',
      `${baseUrl}/api/announcements/stream`,
      (data) => {
        console.log('[AnnouncementStream] 📨 收到新公告:', data.title)

        // 智能去重：避免重复推送
        if (data.id && data.id <= this.lastAnnouncementId) {
          console.log('[AnnouncementStream] 🔄 跳过重复公告')
          return
        }

        if (data.id) {
          this.lastAnnouncementId = data.id
        }

        // 🚀 差异化处理：实时推送 vs 初始数据
        if (data.stream_type === 'realtime_push') {
          // 实时推送的公告 - 强提醒
          wx.showModal({
            title: '📢 新公告推送',
            content: `${data.title}\n\n来自：${data.department}`,
            showCancel: true,
            cancelText: '稍后查看',
            confirmText: '立即查看',
            confirmColor: '#0052d9',
            success: (res) => {
              if (res.confirm && onNewAnnouncement) {
                onNewAnnouncement(data)
              }
            }
          })
        } else {
          // 初始数据 - 静默处理
          if (onNewAnnouncement) onNewAnnouncement(data)
        }
      },
      (error) => {
        console.error('[AnnouncementStream] ❌ 公告流错误:', error)
      }
    )

    this.isActive = true
  }

  stop() {
    console.log('[AnnouncementStream] 🛑 停止公告实时推送')
    this.streamManager.disconnect('announcements')
    this.isActive = false
  }

  /**
   * 📊 获取公告流统计
   */
  getStats() {
    return {
      ...this.streamManager.getConnectionStatus(),
      lastAnnouncementId: this.lastAnnouncementId
    }
  }
}

/**
 * 🎯 活动流式数据管理 - 优化版
 */
class EventStream {
  constructor() {
    this.streamManager = new StreamManager()
    this.isActive = false
    this.participantChangeCount = 0
  }

  start(onEventUpdate) {
    if (this.isActive) {
      console.log('[EventStream] 🎯 活动流已激活')
      return
    }

    console.log('[EventStream] 🚀 启动活动实时更新')
    const baseUrl = getApp().globalData.baseUrl

    this.streamManager.connect(
      'events',
      `${baseUrl}/api/events/stream`,
      (data) => {
        if (data.update_type === 'participant_change') {
          this.participantChangeCount++
          console.log(`[EventStream] 👥 活动 "${data.title}" 参与人数: ${data.current_participants}/${data.max_participants}`)

          // 🎯 用户体验：参与人数变化的动画效果提示
          const changePercent = ((data.current_participants / data.max_participants) * 100).toFixed(1)
          wx.showToast({
            title: `👥 ${data.current_participants}/${data.max_participants} (${changePercent}%)`,
            icon: 'none',
            duration: 2000
          })

        } else if (data.stream_type === 'initial') {
          console.log('[EventStream] 📥 接收初始活动数据:', data.title)
        } else {
          console.log('[EventStream] 🎯 收到活动更新:', data.title)
        }

        if (onEventUpdate) onEventUpdate(data)
      },
      (error) => {
        console.error('[EventStream] ❌ 活动流错误:', error)
      }
    )

    this.isActive = true
  }

  stop() {
    console.log('[EventStream] 🛑 停止活动实时更新')
    this.streamManager.disconnect('events')
    this.isActive = false
  }

  /**
   * 📊 获取活动流统计
   */
  getStats() {
    return {
      ...this.streamManager.getConnectionStatus(),
      participantChanges: this.participantChangeCount
    }
  }
}

// 创建全局实例
const streamManager = new StreamManager()
const announcementStream = new AnnouncementStream()
const eventStream = new EventStream()

module.exports = {
  StreamManager,
  AnnouncementStream,
  EventStream,
  streamManager,
  announcementStream,
  eventStream
} 