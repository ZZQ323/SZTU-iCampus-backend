/**
 * 流式推送和增量同步工具
 * 实现缓存管理、增量同步、事件处理
 */

class StreamManager {
  constructor() {
    this.isOnline = true;
    this.eventSource = null;
    this.lastSyncTime = null;
    this.eventHandlers = new Map();
    this.reconnectTimer = null;
    this.reconnectInterval = 5000; // 5秒重连间隔
    this.maxReconnectAttempts = 10;
    this.reconnectAttempts = 0;
    
    // 缓存配置
    this.cacheKeys = {
      EVENTS: 'sztu_events_cache',
      LAST_SYNC: 'sztu_last_sync_time',
      USER_DATA: 'sztu_user_data_cache',
      ANNOUNCEMENTS: 'sztu_announcements_cache',
      GRADES: 'sztu_grades_cache',
      TRANSACTIONS: 'sztu_transactions_cache',
      SCHEDULE: 'sztu_schedule_cache'
    };
    
    this.init();
  }
  
  /**
   * 初始化流式管理器
   */
  init() {
    console.log('🚀 StreamManager 初始化');
    
    // 监听网络状态变化
    wx.onNetworkStatusChange((res) => {
      this.handleNetworkChange(res);
    });
    
    // 应用启动时立即同步
    this.syncOnAppStart();
  }
  
  /**
   * 应用启动时的同步逻辑
   */
  async syncOnAppStart() {
    try {
      // 1. 立即展示缓存数据
      this.loadCachedData();
      
      // 2. 检查网络状态
      const networkInfo = await this.getNetworkStatus();
      this.isOnline = networkInfo.isConnected;
      
      if (this.isOnline) {
        // 3. 在线时启动增量同步和流式连接
        await this.startIncrementalSync();
        this.connectEventStream();
      } else {
        console.log('📱 离线模式 - 仅显示缓存数据');
      }
      
    } catch (error) {
      console.error('启动同步失败:', error);
    }
  }
  
  /**
   * 加载缓存数据
   */
  loadCachedData() {
    try {
      const cachedEvents = wx.getStorageSync(this.cacheKeys.EVENTS) || [];
      const cachedAnnouncements = wx.getStorageSync(this.cacheKeys.ANNOUNCEMENTS) || [];
      const cachedGrades = wx.getStorageSync(this.cacheKeys.GRADES) || [];
      const cachedTransactions = wx.getStorageSync(this.cacheKeys.TRANSACTIONS) || [];
      
      console.log(`📂 加载缓存数据: ${cachedEvents.length}事件, ${cachedAnnouncements.length}公告, ${cachedGrades.length}成绩, ${cachedTransactions.length}交易`);
      
      // 触发数据更新事件，让各页面显示缓存数据
      this.emitEvent('cache_loaded', {
        events: cachedEvents,
        announcements: cachedAnnouncements,
        grades: cachedGrades,
        transactions: cachedTransactions
      });
      
    } catch (error) {
      console.error('加载缓存数据失败:', error);
    }
  }
  
  /**
   * 启动增量同步
   */
  async startIncrementalSync() {
    try {
      // 获取最后同步时间
      this.lastSyncTime = wx.getStorageSync(this.cacheKeys.LAST_SYNC) || 
                          new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(); // 默认24小时前
      
      console.log(`🔄 开始增量同步 (自 ${this.lastSyncTime})`);
      
      // 调用增量同步API
      const token = wx.getStorageSync('access_token');
      if (!token) {
        console.log('⚠️ 未登录用户，仅同步公开事件');
        return this.syncPublicEvents();
      }
      
      const response = await this.request({
        url: '/stream/sync',
        method: 'GET',
        data: { 
          since: this.lastSyncTime
        },
        header: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.status === 0) {
        await this.processIncrementalData(response.data.events);
        
        // 更新同步时间
        this.updateLastSyncTime(response.data.sync_timestamp);
        
        console.log(`✅ 增量同步完成: ${response.data.count} 个新事件`);
      }
      
    } catch (error) {
      console.error('增量同步失败:', error);
    }
  }

  /**
   * 同步公开事件（未登录用户）
   */
  async syncPublicEvents() {
    try {
      const response = await this.request({
        url: '/stream/sync/guest',
        method: 'GET',
        data: {
          since: this.lastSyncTime
        }
      });
      
      if (response.status === 0) {
        await this.processIncrementalData(response.data.events, true);
        this.updateLastSyncTime(response.data.sync_timestamp);
        console.log(`✅ 公开事件同步完成: ${response.data.count} 个新事件`);
      }
      
    } catch (error) {
      console.error('公开事件同步失败:', error);
    }
  }

  /**
   * 处理增量数据
   */
  async processIncrementalData(newEvents, isPublicOnly = false) {
    if (!newEvents || newEvents.length === 0) {
      return;
    }
    
    // 按事件类型分类处理
    const eventsByType = this.groupEventsByType(newEvents);
    
    // 更新各类数据缓存
    for (const [eventType, events] of Object.entries(eventsByType)) {
      await this.updateCacheByEventType(eventType, events);
    }
    
    // 触发UI更新事件
    this.emitEvent('incremental_sync', {
      newEvents: newEvents,
      eventsByType: eventsByType,
      isPublicOnly: isPublicOnly
    });
  }
  
  /**
   * 按事件类型分组
   */
  groupEventsByType(events) {
    const grouped = {};
    
    events.forEach(event => {
      const type = event.event_type;
      if (!grouped[type]) {
        grouped[type] = [];
      }
      grouped[type].push(event);
    });
    
    return grouped;
  }
  
  /**
   * 根据事件类型更新缓存
   */
  async updateCacheByEventType(eventType, events) {
    try {
      switch (eventType) {
        case 'announcement':
        case 'notice':
        case 'system_message':
          await this.updateAnnouncementsCache(events);
          break;
          
        case 'grade_update':
          await this.updateGradesCache(events);
          break;
          
        case 'transaction':
          await this.updateTransactionsCache(events);
          break;
          
        case 'course_change':
          await this.updateScheduleCache(events);
          break;
          
        case 'library_reminder':
          await this.updateLibraryCache(events);
          break;
          
        default:
          // 通用事件缓存
          await this.updateEventsCache(events);
      }
      
    } catch (error) {
      console.error(`更新 ${eventType} 缓存失败:`, error);
    }
  }

  /**
   * 更新公告缓存
   */
  async updateAnnouncementsCache(events) {
    const cached = wx.getStorageSync(this.cacheKeys.ANNOUNCEMENTS) || [];
    
    events.forEach(event => {
      const announcement = {
        id: event.event_id,
        title: event.data.title,
        content: event.data.content,
        department: event.data.department,
        timestamp: event.timestamp,
        urgent: event.data.urgent || false,
        category: event.data.category || 'general'
      };
      
      // 避免重复
      const existing = cached.find(item => item.id === announcement.id);
      if (!existing) {
        cached.unshift(announcement); // 新消息在前
      }
    });
    
    // 保持缓存大小限制
    if (cached.length > 100) {
      cached.splice(100);
    }
    
    wx.setStorageSync(this.cacheKeys.ANNOUNCEMENTS, cached);
  }
  
  /**
   * 更新成绩缓存
   */
  async updateGradesCache(events) {
    const cached = wx.getStorageSync(this.cacheKeys.GRADES) || [];
    
    events.forEach(event => {
      const grade = {
        id: event.event_id,
        course_name: event.data.course_name,
        score: event.data.score,
        grade_level: event.data.grade_level,
        semester: event.data.semester,
        timestamp: event.timestamp,
        is_new: true // 标记为新成绩
      };
      
      // 检查是否已存在相同课程的成绩
      const existingIndex = cached.findIndex(item => 
        item.course_name === grade.course_name && 
        item.semester === grade.semester
      );
      
      if (existingIndex >= 0) {
        // 更新现有成绩
        cached[existingIndex] = grade;
    } else {
        // 添加新成绩
        cached.unshift(grade);
      }
    });
    
    wx.setStorageSync(this.cacheKeys.GRADES, cached);
  }
  
  /**
   * 更新交易缓存
   */
  async updateTransactionsCache(events) {
    const cached = wx.getStorageSync(this.cacheKeys.TRANSACTIONS) || [];
    
    events.forEach(event => {
      const transaction = {
        id: event.event_id,
        amount: event.data.amount,
        location: event.data.location,
        balance: event.data.balance,
        time: event.data.time,
        timestamp: event.timestamp,
        is_new: true // 标记为新交易
      };
      
      // 避免重复
      const existing = cached.find(item => item.id === transaction.id);
      if (!existing) {
        cached.unshift(transaction);
      }
    });
    
    // 保持缓存大小限制（最近200条交易）
    if (cached.length > 200) {
      cached.splice(200);
    }
    
    wx.setStorageSync(this.cacheKeys.TRANSACTIONS, cached);
  }
  
  /**
   * 更新课表缓存
   */
  async updateScheduleCache(events) {
    const cached = wx.getStorageSync(this.cacheKeys.SCHEDULE) || {};
    
    events.forEach(event => {
      const courseChange = {
        id: event.event_id,
        course_name: event.data.course_name,
        teacher: event.data.teacher,
        change_type: event.data.change_type,
        old_schedule: event.data.old_schedule,
        new_schedule: event.data.new_schedule,
        reason: event.data.reason,
        effective_date: event.data.effective_date,
        timestamp: event.timestamp
      };
      
      // 更新课表变更记录
      if (!cached.changes) {
        cached.changes = [];
      }
      cached.changes.unshift(courseChange);
      
      // 标记需要刷新课表
      cached.needs_refresh = true;
      cached.last_change = event.timestamp;
    });
    
    wx.setStorageSync(this.cacheKeys.SCHEDULE, cached);
  }
  
  /**
   * 更新图书馆缓存
   */
  async updateLibraryCache(events) {
    const cached = wx.getStorageSync('sztu_library_cache') || [];
    
    events.forEach(event => {
      const libraryReminder = {
        id: event.event_id,
        book_title: event.data.book_title,
        due_date: event.data.due_date,
        days_left: event.data.days_left,
        fine_amount: event.data.fine_amount,
        action_required: event.data.action_required,
        timestamp: event.timestamp,
        is_new: true
      };
      
      // 避免重复
      const existing = cached.find(item => item.id === libraryReminder.id);
      if (!existing) {
        cached.unshift(libraryReminder);
      }
    });
    
    // 保持缓存大小限制
    if (cached.length > 50) {
      cached.splice(50);
    }
    
    wx.setStorageSync('sztu_library_cache', cached);
  }
  
  /**
   * 更新通用事件缓存
   */
  async updateEventsCache(events) {
    const cached = wx.getStorageSync(this.cacheKeys.EVENTS) || [];
    
    events.forEach(event => {
      // 避免重复
      const existing = cached.find(item => item.event_id === event.event_id);
      if (!existing) {
        cached.unshift(event);
      }
    });
    
    // 保持缓存大小限制
    if (cached.length > 300) {
      cached.splice(300);
    }
    
    wx.setStorageSync(this.cacheKeys.EVENTS, cached);
  }
  
  /**
   * 连接事件流（当前为模拟实现）
   */
  connectEventStream() {
    console.log('🔗 模拟连接事件流');
    // 注意：真实的微信小程序环境可能需要使用WebSocket或长轮询
    // 这里为了简化，暂时只是模拟连接状态
  }
  
  /**
   * 处理网络状态变化
   */
  async handleNetworkChange(networkInfo) {
    const wasOnline = this.isOnline;
    this.isOnline = networkInfo.isConnected;
    
    console.log(`🌐 网络状态变化: ${wasOnline ? '在线' : '离线'} -> ${this.isOnline ? '在线' : '离线'}`);
    
    if (!wasOnline && this.isOnline) {
      // 从离线转为在线：启动增量同步
      console.log('🔄 网络恢复，启动增量同步...');
      await this.startIncrementalSync();
      this.connectEventStream();
      
    } else if (wasOnline && !this.isOnline) {
      // 从在线转为离线：进入离线模式
      console.log('📱 网络断开，进入离线模式');
    }
    
    // 通知应用网络状态变化
    this.emitEvent('network_change', {
      isOnline: this.isOnline,
      wasOnline: wasOnline
    });
  }
  
  /**
   * 获取网络状态
   */
  getNetworkStatus() {
    return new Promise((resolve) => {
      wx.getNetworkType({
        success: (res) => {
          resolve({
            networkType: res.networkType,
            isConnected: res.networkType !== 'none'
          });
        },
        fail: () => {
          resolve({
            networkType: 'unknown',
            isConnected: false
          });
        }
      });
    });
  }
  
  /**
   * 更新最后同步时间
   */
  updateLastSyncTime(timestamp) {
    this.lastSyncTime = timestamp;
    wx.setStorageSync(this.cacheKeys.LAST_SYNC, timestamp);
  }
  
  /**
   * 通用请求方法
   */
  request(options) {
    const baseUrl = getApp().globalData.apiBaseUrl || 'http://localhost:8000';
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${baseUrl}/api/v1${options.url}`,
        method: options.method || 'GET',
        data: options.data,
        header: {
          'Content-Type': 'application/json',
          ...options.header
        },
            success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data);
        } else {
            reject(new Error(`HTTP ${res.statusCode}: ${res.data?.msg || 'Unknown error'}`));
          }
        },
        fail: reject
      });
    });
  }
  
  /**
   * 事件发射器
   */
  emitEvent(eventName, data) {
    const handlers = this.eventHandlers.get(eventName) || [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error(`事件处理器错误 [${eventName}]:`, error);
      }
    });
  }
  
  /**
   * 注册事件监听器
   */
  addEventListener(eventName, handler) {
    if (!this.eventHandlers.has(eventName)) {
      this.eventHandlers.set(eventName, []);
    }
    this.eventHandlers.get(eventName).push(handler);
  }
  
  /**
   * 移除事件监听器
   */
  removeEventListener(eventName, handler) {
    const handlers = this.eventHandlers.get(eventName) || [];
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
    }
  }
  
  /**
   * 手动触发增量同步
   */
  async manualSync() {
    console.log('🔄 手动触发增量同步');
    await this.startIncrementalSync();
  }
  
  /**
   * 清除缓存
   */
  clearCache() {
    Object.values(this.cacheKeys).forEach(key => {
      wx.removeStorageSync(key);
    });
    console.log('🗑️ 缓存已清除');
  }
  
  /**
   * 获取缓存统计
   */
  getCacheStats() {
    const stats = {};
    Object.entries(this.cacheKeys).forEach(([name, key]) => {
      try {
        const data = wx.getStorageSync(key);
        stats[name] = {
          exists: !!data,
          size: data ? JSON.stringify(data).length : 0,
          count: Array.isArray(data) ? data.length : (data ? 1 : 0)
        };
      } catch (error) {
        stats[name] = { exists: false, size: 0, count: 0, error: error.message };
      }
    });
    
    return stats;
  }
}

// 创建全局实例
const streamManager = new StreamManager();

// 导出
module.exports = {
  StreamManager,
  streamManager
}; 