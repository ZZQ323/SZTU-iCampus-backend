/**
 * 存储管理器
 * 统一本地存储接口，提供加密、过期时间、数据验证等功能
 * 确保数据安全性和一致性
 */
class StorageManager {
  
  static PREFIX = 'iCampus_'
  static DEFAULT_TTL = 24 * 60 * 60 * 1000 // 24小时
  
  /**
   * 构建存储键名
   * @param {string} key 原始键名
   * @returns {string} 完整键名
   */
  static buildKey(key) {
    return `${this.PREFIX}${key}`
  }

  /**
   * 设置数据
   * @param {string} key 键名
   * @param {*} value 值
   * @param {Object} options 选项
   * @returns {boolean} 是否成功
   */
  static set(key, value, options = {}) {
    try {
      const { 
        ttl = this.DEFAULT_TTL, 
        encrypt = false,
        sync = true 
      } = options
      
      const data = {
        value: encrypt ? this.encrypt(value) : value,
        timestamp: Date.now(),
        ttl: ttl,
        encrypted: encrypt
      }
      
      const storageKey = this.buildKey(key)
      
      if (sync) {
        wx.setStorageSync(storageKey, data)
      } else {
        wx.setStorage({
          key: storageKey,
          data: data
        })
      }
      
      console.log(`[StorageManager] ✅ 设置存储:`, key)
      return true
    } catch (error) {
      console.error(`[StorageManager] ❌ 设置存储失败:`, key, error)
      return false
    }
  }

  /**
   * 获取数据
   * @param {string} key 键名
   * @param {*} defaultValue 默认值
   * @param {boolean} sync 是否同步获取
   * @returns {*} 存储值或默认值
   */
  static get(key, defaultValue = null, sync = true) {
    try {
      const storageKey = this.buildKey(key)
      
      let data
      if (sync) {
        data = wx.getStorageSync(storageKey)
      } else {
        // 异步版本需要返回Promise
        return new Promise((resolve) => {
          wx.getStorage({
            key: storageKey,
            success: (res) => {
              const result = this.processStoredData(res.data, key, defaultValue)
              resolve(result)
            },
            fail: () => {
              console.log(`[StorageManager] 📭 获取存储失败，使用默认值:`, key)
              resolve(defaultValue)
            }
          })
        })
      }
      
      return this.processStoredData(data, key, defaultValue)
    } catch (error) {
      console.error(`[StorageManager] ❌ 获取存储失败:`, key, error)
      return defaultValue
    }
  }

  /**
   * 处理存储的数据
   * @param {*} data 存储数据
   * @param {string} key 键名
   * @param {*} defaultValue 默认值
   * @returns {*} 处理后的值
   */
  static processStoredData(data, key, defaultValue) {
    if (!data) {
      console.log(`[StorageManager] 📭 存储为空，使用默认值:`, key)
      return defaultValue
    }
    
    // 检查是否是新格式的数据（包含元数据）
    if (typeof data === 'object' && data.timestamp !== undefined) {
      // 检查是否过期
      if (data.ttl && data.ttl > 0) {
        const isExpired = Date.now() - data.timestamp > data.ttl
        if (isExpired) {
          console.log(`[StorageManager] ⏰ 存储已过期:`, key)
          this.remove(key)
          return defaultValue
        }
      }
      
      // 解密数据
      const value = data.encrypted ? this.decrypt(data.value) : data.value
      console.log(`[StorageManager] 📖 获取存储:`, key)
      return value
    } else {
      // 兼容旧格式数据
      console.log(`[StorageManager] 📖 获取存储(兼容格式):`, key)
      return data
    }
  }

  /**
   * 删除数据
   * @param {string} key 键名
   * @param {boolean} sync 是否同步删除
   * @returns {boolean} 是否成功
   */
  static remove(key, sync = true) {
    try {
      const storageKey = this.buildKey(key)
      
      if (sync) {
        wx.removeStorageSync(storageKey)
      } else {
        wx.removeStorage({ key: storageKey })
      }
      
      console.log(`[StorageManager] 🗑️ 删除存储:`, key)
      return true
    } catch (error) {
      console.error(`[StorageManager] ❌ 删除存储失败:`, key, error)
      return false
    }
  }

  /**
   * 检查键是否存在
   * @param {string} key 键名
   * @returns {boolean} 是否存在
   */
  static has(key) {
    try {
      const value = this.get(key, Symbol('not_found'))
      return value !== Symbol('not_found')
    } catch (error) {
      return false
    }
  }

  /**
   * 清除所有应用数据
   * @param {boolean} keepUserInfo 是否保留用户信息
   * @returns {boolean} 是否成功
   */
  static clear(keepUserInfo = false) {
    try {
      const { keys } = wx.getStorageInfoSync()
      const appKeys = keys.filter(key => key.startsWith(this.PREFIX))
      
      const keysToRemove = keepUserInfo 
        ? appKeys.filter(key => !key.includes('userInfo') && !key.includes('token'))
        : appKeys
      
      keysToRemove.forEach(key => {
        wx.removeStorageSync(key)
      })
      
      console.log(`[StorageManager] 🧹 清除存储完成，共清除 ${keysToRemove.length} 项`)
      return true
    } catch (error) {
      console.error(`[StorageManager] ❌ 清除存储失败:`, error)
      return false
    }
  }

  /**
   * 获取存储信息
   * @returns {Object} 存储信息
   */
  static getInfo() {
    try {
      const info = wx.getStorageInfoSync()
      const appKeys = info.keys.filter(key => key.startsWith(this.PREFIX))
      
      return {
        totalKeys: info.keys.length,
        appKeys: appKeys.length,
        currentSize: info.currentSize,
        limitSize: info.limitSize,
        usage: `${((info.currentSize / info.limitSize) * 100).toFixed(2)}%`
      }
    } catch (error) {
      console.error(`[StorageManager] ❌ 获取存储信息失败:`, error)
      return null
    }
  }

  // ===== 用户相关存储 =====

  /**
   * 设置用户信息
   * @param {Object} userInfo 用户信息
   * @returns {boolean} 是否成功
   */
  static setUserInfo(userInfo) {
    return this.set('userInfo', userInfo, {
      ttl: 7 * 24 * 60 * 60 * 1000, // 7天
      encrypt: true
    })
  }

  /**
   * 获取用户信息
   * @returns {Object|null} 用户信息
   */
  static getUserInfo() {
    return this.get('userInfo', null)
  }

  /**
   * 设置登录令牌
   * @param {string} token 令牌
   * @returns {boolean} 是否成功
   */
  static setToken(token) {
    return this.set('token', token, {
      ttl: 30 * 24 * 60 * 60 * 1000, // 30天
      encrypt: true
    })
  }

  /**
   * 获取登录令牌
   * @returns {string|null} 令牌
   */
  static getToken() {
    return this.get('token', null)
  }

  /**
   * 清除用户数据
   * @returns {boolean} 是否成功
   */
  static clearUserData() {
    const success1 = this.remove('userInfo')
    const success2 = this.remove('token')
    return success1 && success2
  }

  // ===== 应用设置 =====

  /**
   * 设置应用配置
   * @param {string} key 配置键
   * @param {*} value 配置值
   * @returns {boolean} 是否成功
   */
  static setSetting(key, value) {
    return this.set(`setting_${key}`, value, {
      ttl: 0 // 永不过期
    })
  }

  /**
   * 获取应用配置
   * @param {string} key 配置键
   * @param {*} defaultValue 默认值
   * @returns {*} 配置值
   */
  static getSetting(key, defaultValue = null) {
    return this.get(`setting_${key}`, defaultValue)
  }

  /**
   * 批量设置配置
   * @param {Object} settings 配置对象
   * @returns {boolean} 是否成功
   */
  static setSettings(settings) {
    try {
      Object.entries(settings).forEach(([key, value]) => {
        this.setSetting(key, value)
      })
      return true
    } catch (error) {
      console.error(`[StorageManager] ❌ 批量设置配置失败:`, error)
      return false
    }
  }

  // ===== 缓存管理 =====

  /**
   * 设置缓存
   * @param {string} key 缓存键
   * @param {*} data 数据
   * @param {number} ttl 过期时间(毫秒)
   * @returns {boolean} 是否成功
   */
  static setCache(key, data, ttl = 5 * 60 * 1000) {
    return this.set(`cache_${key}`, data, { ttl })
  }

  /**
   * 获取缓存
   * @param {string} key 缓存键
   * @param {*} defaultValue 默认值
   * @returns {*} 缓存数据
   */
  static getCache(key, defaultValue = null) {
    return this.get(`cache_${key}`, defaultValue)
  }

  /**
   * 清除所有缓存
   * @returns {boolean} 是否成功
   */
  static clearCache() {
    try {
      const { keys } = wx.getStorageInfoSync()
      const cacheKeys = keys.filter(key => key.startsWith(`${this.PREFIX}cache_`))
      
      cacheKeys.forEach(key => {
        wx.removeStorageSync(key)
      })
      
      console.log(`[StorageManager] 🧹 清除缓存完成，共清除 ${cacheKeys.length} 项`)
      return true
    } catch (error) {
      console.error(`[StorageManager] ❌ 清除缓存失败:`, error)
      return false
    }
  }

  // ===== 数据加密/解密 =====

  /**
   * 简单加密（Base64编码 + 位移）
   * @param {*} data 原始数据
   * @returns {string} 加密后的字符串
   */
  static encrypt(data) {
    try {
      const jsonString = JSON.stringify(data)
      const base64 = wx.arrayBufferToBase64(this.stringToArrayBuffer(jsonString))
      
      // 简单的字符位移
      return base64.split('').map(char => 
        String.fromCharCode(char.charCodeAt(0) + 1)
      ).join('')
    } catch (error) {
      console.warn(`[StorageManager] 加密失败，使用原始数据:`, error)
      return data
    }
  }

  /**
   * 简单解密
   * @param {string} encryptedData 加密的数据
   * @returns {*} 解密后的数据
   */
  static decrypt(encryptedData) {
    try {
      // 还原字符位移
      const base64 = encryptedData.split('').map(char => 
        String.fromCharCode(char.charCodeAt(0) - 1)
      ).join('')
      
      const arrayBuffer = wx.base64ToArrayBuffer(base64)
      const jsonString = this.arrayBufferToString(arrayBuffer)
      
      return JSON.parse(jsonString)
    } catch (error) {
      console.warn(`[StorageManager] 解密失败，返回原始数据:`, error)
      return encryptedData
    }
  }

  /**
   * 字符串转ArrayBuffer
   * @param {string} str 字符串
   * @returns {ArrayBuffer} ArrayBuffer
   */
  static stringToArrayBuffer(str) {
    const buffer = new ArrayBuffer(str.length)
    const view = new Uint8Array(buffer)
    for (let i = 0; i < str.length; i++) {
      view[i] = str.charCodeAt(i)
    }
    return buffer
  }

  /**
   * ArrayBuffer转字符串
   * @param {ArrayBuffer} buffer ArrayBuffer
   * @returns {string} 字符串
   */
  static arrayBufferToString(buffer) {
    const view = new Uint8Array(buffer)
    return String.fromCharCode.apply(null, view)
  }

  // ===== 数据迁移 =====

  /**
   * 迁移旧版本数据
   * @param {string} version 版本号
   * @returns {boolean} 是否需要迁移
   */
  static migrateData(version) {
    const currentVersion = this.getSetting('dataVersion', '1.0.0')
    
    if (currentVersion === version) {
      return false
    }
    
    console.log(`[StorageManager] 🔄 开始数据迁移: ${currentVersion} -> ${version}`)
    
    try {
      // 这里可以添加具体的迁移逻辑
      // 例如：格式转换、键名变更等
      
      this.setSetting('dataVersion', version)
      console.log(`[StorageManager] ✅ 数据迁移完成`)
      return true
    } catch (error) {
      console.error(`[StorageManager] ❌ 数据迁移失败:`, error)
      return false
    }
  }
}

module.exports = StorageManager 