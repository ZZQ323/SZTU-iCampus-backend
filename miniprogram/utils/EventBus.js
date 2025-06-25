/**
 * 事件总线
 * 提供全局事件通信机制，实现页面和组件间的松耦合通信
 * 支持事件监听、触发、一次性监听、命名空间等功能
 */
class EventBus {
  
  constructor() {
    this.events = new Map()
    this.onceEvents = new Map()
    this.namespaces = new Map()
    this.maxListeners = 10
    this.debug = false
  }

  /**
   * 设置调试模式
   * @param {boolean} enable 是否启用调试
   */
  setDebug(enable) {
    this.debug = enable
  }

  /**
   * 日志输出
   * @param {string} type 日志类型
   * @param {string} message 消息
   * @param {...any} args 其他参数
   */
  log(type, message, ...args) {
    if (this.debug) {
      console.log(`[EventBus] ${type}:`, message, ...args)
    }
  }

  /**
   * 监听事件
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   * @param {Object} context 上下文对象
   * @returns {Function} 取消监听的函数
   */
  on(eventName, callback, context = null) {
    if (!eventName || typeof callback !== 'function') {
      throw new Error('事件名称和回调函数都是必需的')
    }

    if (!this.events.has(eventName)) {
      this.events.set(eventName, [])
    }

    const listeners = this.events.get(eventName)
    
    // 检查监听器数量限制
    if (listeners.length >= this.maxListeners) {
      console.warn(`[EventBus] ⚠️ 事件 "${eventName}" 的监听器数量已达到限制 (${this.maxListeners})`)
    }

    const listener = {
      callback,
      context,
      id: this.generateId()
    }

    listeners.push(listener)
    this.log('📡', `监听事件: ${eventName}`, listener.id)

    // 返回取消监听的函数
    return () => this.off(eventName, callback, context)
  }

  /**
   * 监听事件（一次性）
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   * @param {Object} context 上下文对象
   * @returns {Function} 取消监听的函数
   */
  once(eventName, callback, context = null) {
    if (!eventName || typeof callback !== 'function') {
      throw new Error('事件名称和回调函数都是必需的')
    }

    const listener = {
      callback,
      context,
      id: this.generateId()
    }

    if (!this.onceEvents.has(eventName)) {
      this.onceEvents.set(eventName, [])
    }

    this.onceEvents.get(eventName).push(listener)
    this.log('📡', `一次性监听事件: ${eventName}`, listener.id)

    // 返回取消监听的函数
    return () => this.offOnce(eventName, callback, context)
  }

  /**
   * 取消事件监听
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   * @param {Object} context 上下文对象
   */
  off(eventName, callback = null, context = null) {
    if (!this.events.has(eventName)) {
      return
    }

    const listeners = this.events.get(eventName)

    if (!callback) {
      // 如果没有指定回调函数，则移除所有监听器
      this.events.delete(eventName)
      this.log('🔇', `移除所有监听器: ${eventName}`)
      return
    }

    const newListeners = listeners.filter(listener => {
      const shouldRemove = listener.callback === callback && 
                          (context === null || listener.context === context)
      
      if (shouldRemove) {
        this.log('🔇', `移除监听器: ${eventName}`, listener.id)
      }
      
      return !shouldRemove
    })

    if (newListeners.length === 0) {
      this.events.delete(eventName)
    } else {
      this.events.set(eventName, newListeners)
    }
  }

  /**
   * 取消一次性事件监听
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   * @param {Object} context 上下文对象
   */
  offOnce(eventName, callback = null, context = null) {
    if (!this.onceEvents.has(eventName)) {
      return
    }

    const listeners = this.onceEvents.get(eventName)

    if (!callback) {
      this.onceEvents.delete(eventName)
      this.log('🔇', `移除所有一次性监听器: ${eventName}`)
      return
    }

    const newListeners = listeners.filter(listener => {
      const shouldRemove = listener.callback === callback && 
                          (context === null || listener.context === context)
      
      if (shouldRemove) {
        this.log('🔇', `移除一次性监听器: ${eventName}`, listener.id)
      }
      
      return !shouldRemove
    })

    if (newListeners.length === 0) {
      this.onceEvents.delete(eventName)
    } else {
      this.onceEvents.set(eventName, newListeners)
    }
  }

  /**
   * 触发事件
   * @param {string} eventName 事件名称
   * @param {...any} args 传递给监听器的参数
   * @returns {number} 被触发的监听器数量
   */
  emit(eventName, ...args) {
    if (!eventName) {
      throw new Error('事件名称是必需的')
    }

    let count = 0

    this.log('📢', `触发事件: ${eventName}`, args)

    // 触发普通监听器
    if (this.events.has(eventName)) {
      const listeners = [...this.events.get(eventName)] // 创建副本，防止在回调中修改数组
      
      listeners.forEach(listener => {
        try {
          if (listener.context) {
            listener.callback.call(listener.context, ...args)
          } else {
            listener.callback(...args)
          }
          count++
        } catch (error) {
          console.error(`[EventBus] ❌ 事件回调执行失败: ${eventName}`, error)
        }
      })
    }

    // 触发一次性监听器
    if (this.onceEvents.has(eventName)) {
      const onceListeners = [...this.onceEvents.get(eventName)]
      this.onceEvents.delete(eventName) // 立即删除，防止重复触发

      onceListeners.forEach(listener => {
        try {
          if (listener.context) {
            listener.callback.call(listener.context, ...args)
          } else {
            listener.callback(...args)
          }
          count++
        } catch (error) {
          console.error(`[EventBus] ❌ 一次性事件回调执行失败: ${eventName}`, error)
        }
      })
    }

    this.log('✅', `事件触发完成: ${eventName}`, `${count} 个监听器`)
    return count
  }

  /**
   * 异步触发事件
   * @param {string} eventName 事件名称
   * @param {...any} args 传递给监听器的参数
   * @returns {Promise<number>} 被触发的监听器数量
   */
  async emitAsync(eventName, ...args) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const count = this.emit(eventName, ...args)
        resolve(count)
      }, 0)
    })
  }

  /**
   * 获取事件的监听器数量
   * @param {string} eventName 事件名称
   * @returns {number} 监听器数量
   */
  listenerCount(eventName) {
    const regularCount = this.events.has(eventName) ? this.events.get(eventName).length : 0
    const onceCount = this.onceEvents.has(eventName) ? this.onceEvents.get(eventName).length : 0
    
    return regularCount + onceCount
  }

  /**
   * 获取所有事件名称
   * @returns {Array<string>} 事件名称列表
   */
  eventNames() {
    const regularEvents = Array.from(this.events.keys())
    const onceEvents = Array.from(this.onceEvents.keys())
    
    return [...new Set([...regularEvents, ...onceEvents])]
  }

  /**
   * 移除所有监听器
   * @param {string} eventName 可选，指定事件名称
   */
  removeAllListeners(eventName = null) {
    if (eventName) {
      this.events.delete(eventName)
      this.onceEvents.delete(eventName)
      this.log('🧹', `清除所有监听器: ${eventName}`)
    } else {
      this.events.clear()
      this.onceEvents.clear()
      this.namespaces.clear()
      this.log('🧹', `清除所有监听器`)
    }
  }

  /**
   * 创建命名空间
   * @param {string} namespace 命名空间名称
   * @returns {Object} 命名空间对象
   */
  namespace(namespace) {
    if (!namespace) {
      throw new Error('命名空间名称是必需的')
    }

    if (this.namespaces.has(namespace)) {
      return this.namespaces.get(namespace)
    }

    const ns = {
      on: (eventName, callback, context) => {
        return this.on(`${namespace}:${eventName}`, callback, context)
      },
      
      once: (eventName, callback, context) => {
        return this.once(`${namespace}:${eventName}`, callback, context)
      },
      
      off: (eventName, callback, context) => {
        this.off(`${namespace}:${eventName}`, callback, context)
      },
      
      emit: (eventName, ...args) => {
        return this.emit(`${namespace}:${eventName}`, ...args)
      },
      
      emitAsync: (eventName, ...args) => {
        return this.emitAsync(`${namespace}:${eventName}`, ...args)
      },
      
      clear: () => {
        const eventNames = this.eventNames()
        const namespaceEvents = eventNames.filter(name => name.startsWith(`${namespace}:`))
        
        namespaceEvents.forEach(eventName => {
          this.removeAllListeners(eventName)
        })
        
        this.log('🧹', `清除命名空间: ${namespace}`)
      }
    }

    this.namespaces.set(namespace, ns)
    this.log('📁', `创建命名空间: ${namespace}`)
    
    return ns
  }

  /**
   * 生成唯一ID
   * @returns {string} 唯一ID
   */
  generateId() {
    return Math.random().toString(36).substr(2, 9)
  }

  /**
   * 设置最大监听器数量
   * @param {number} count 最大数量
   */
  setMaxListeners(count) {
    this.maxListeners = Math.max(1, parseInt(count) || 10)
  }

  /**
   * 获取调试信息
   * @returns {Object} 调试信息
   */
  getDebugInfo() {
    const regularEvents = {}
    const onceEvents = {}

    this.events.forEach((listeners, eventName) => {
      regularEvents[eventName] = listeners.length
    })

    this.onceEvents.forEach((listeners, eventName) => {
      onceEvents[eventName] = listeners.length
    })

    return {
      regularEvents,
      onceEvents,
      namespaces: Array.from(this.namespaces.keys()),
      totalListeners: Object.values(regularEvents).reduce((sum, count) => sum + count, 0) +
                     Object.values(onceEvents).reduce((sum, count) => sum + count, 0)
    }
  }
}

// 创建全局实例
const eventBus = new EventBus()

// 预定义一些常用事件
const Events = {
  // 用户相关
  USER_LOGIN: 'user:login',
  USER_LOGOUT: 'user:logout',
  USER_INFO_UPDATE: 'user:info_update',
  
  // 数据更新
  DATA_REFRESH: 'data:refresh',
  DATA_UPDATE: 'data:update',
  DATA_ERROR: 'data:error',
  
  // 页面相关
  PAGE_SHOW: 'page:show',
  PAGE_HIDE: 'page:hide',
  PAGE_LOAD: 'page:load',
  
  // 网络相关
  NETWORK_CHANGE: 'network:change',
  NETWORK_ERROR: 'network:error',
  
  // 推送相关
  PUSH_RECEIVE: 'push:receive',
  PUSH_CLICK: 'push:click',
  
  // 业务相关
  ANNOUNCEMENT_NEW: 'announcement:new',
  SCHEDULE_UPDATE: 'schedule:update',
  GRADE_UPDATE: 'grade:update',
  CARD_TRANSACTION: 'card:transaction'
}

module.exports = {
  EventBus,
  eventBus,
  Events
} 