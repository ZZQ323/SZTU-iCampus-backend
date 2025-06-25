const DataProcessor = require('./DataProcessor')

/**
 * 资源客户端基类
 * 统一API调用模式，提供标准化的CRUD接口
 * 消除各页面中重复的API调用逻辑
 */
class ResourceClient {
  constructor(baseUrl = '', resourceName = '') {
    this.baseUrl = baseUrl
    this.resourceName = resourceName
    this.baseAPI = getApp().globalData.api // 使用全局API配置
  }

  /**
   * 构建完整的请求URL
   * @param {string} endpoint 端点路径
   * @returns {string} 完整URL
   */
  buildUrl(endpoint = '') {
    if (endpoint.startsWith('http')) return endpoint
    return `${this.baseUrl}${endpoint}`
  }

  /**
   * 获取授权头
   * @returns {Object} 授权头信息
   */
  getAuthHeaders() {
    const token = wx.getStorageSync('token')
    return token ? { 'Authorization': `Bearer ${token}` } : {}
  }

  /**
   * 标准化请求配置
   * @param {Object} options 请求选项
   * @returns {Object} 标准化后的请求配置
   */
  normalizeRequestOptions(options = {}) {
    return {
      method: 'GET',
      data: {},
      header: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...options.header
      },
      timeout: 30000,
      ...options
    }
  }

  /**
   * 通用HTTP请求方法
   * @param {string} url 请求URL
   * @param {Object} options 请求选项
   * @returns {Promise} 请求Promise
   */
  request(url, options = {}) {
    const config = this.normalizeRequestOptions(options)
    const fullUrl = this.buildUrl(url)
    
    console.log(`[${this.constructor.name}] 🔗 请求:`, config.method, fullUrl)
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: fullUrl,
        ...config,
        success: (res) => {
          console.log(`[${this.constructor.name}] ✅ 响应:`, res.statusCode, res.data)
          
          if (res.statusCode >= 200 && res.statusCode < 300) {
            try {
              const processedData = DataProcessor.processAPIResponse(res.data)
              resolve(processedData)
            } catch (error) {
              console.error(`[${this.constructor.name}] 数据处理错误:`, error)
              reject(error)
            }
          } else {
            const error = new Error(`HTTP ${res.statusCode}: ${res.data?.message || '请求失败'}`)
            console.error(`[${this.constructor.name}] ❌ HTTP错误:`, error.message)
            reject(error)
          }
        },
        fail: (error) => {
          console.error(`[${this.constructor.name}] ❌ 网络错误:`, error)
          const networkError = new Error('网络连接失败，请检查网络设置')
          reject(networkError)
        }
      })
    })
  }

  // ===== 标准CRUD操作 =====

  /**
   * 获取资源列表
   * @param {Object} params 查询参数
   * @returns {Promise<Array>} 资源列表
   */
  async getList(params = {}) {
    const queryString = this.buildQueryString(params)
    const endpoint = `/${this.resourceName}${queryString}`
    return this.request(endpoint, { method: 'GET' })
  }

  /**
   * 获取分页列表
   * @param {Object} params 分页参数
   * @returns {Promise<Object>} 分页数据
   */
  async getPaginatedList(params = {}) {
    const defaultParams = {
      page: 1,
      pageSize: 20,
      ...params
    }
    
    const queryString = this.buildQueryString(defaultParams)
    const endpoint = `/${this.resourceName}${queryString}`
    return this.request(endpoint, { method: 'GET' })
  }

  /**
   * 根据ID获取单个资源
   * @param {string|number} id 资源ID
   * @returns {Promise<Object>} 资源详情
   */
  async getById(id) {
    if (!id) throw new Error('资源ID不能为空')
    
    const endpoint = `/${this.resourceName}/${id}`
    return this.request(endpoint, { method: 'GET' })
  }

  /**
   * 创建新资源
   * @param {Object} data 资源数据
   * @returns {Promise<Object>} 创建结果
   */
  async create(data) {
    if (!data || typeof data !== 'object') {
      throw new Error('创建数据不能为空')
    }
    
    const endpoint = `/${this.resourceName}`
    return this.request(endpoint, {
      method: 'POST',
      data: data
    })
  }

  /**
   * 更新资源
   * @param {string|number} id 资源ID
   * @param {Object} data 更新数据
   * @returns {Promise<Object>} 更新结果
   */
  async update(id, data) {
    if (!id) throw new Error('资源ID不能为空')
    if (!data || typeof data !== 'object') {
      throw new Error('更新数据不能为空')
    }
    
    const endpoint = `/${this.resourceName}/${id}`
    return this.request(endpoint, {
      method: 'PUT',
      data: data
    })
  }

  /**
   * 部分更新资源
   * @param {string|number} id 资源ID
   * @param {Object} data 更新数据
   * @returns {Promise<Object>} 更新结果
   */
  async patch(id, data) {
    if (!id) throw new Error('资源ID不能为空')
    if (!data || typeof data !== 'object') {
      throw new Error('更新数据不能为空')
    }
    
    const endpoint = `/${this.resourceName}/${id}`
    return this.request(endpoint, {
      method: 'PATCH',
      data: data
    })
  }

  /**
   * 删除资源
   * @param {string|number} id 资源ID
   * @returns {Promise<Object>} 删除结果
   */
  async delete(id) {
    if (!id) throw new Error('资源ID不能为空')
    
    const endpoint = `/${this.resourceName}/${id}`
    return this.request(endpoint, { method: 'DELETE' })
  }

  // ===== 通用查询操作 =====

  /**
   * 搜索资源
   * @param {string} keyword 搜索关键词
   * @param {Object} options 搜索选项
   * @returns {Promise<Array>} 搜索结果
   */
  async search(keyword, options = {}) {
    const params = {
      q: keyword,
      search: keyword,
      ...options
    }
    
    const queryString = this.buildQueryString(params)
    const endpoint = `/${this.resourceName}/search${queryString}`
    return this.request(endpoint, { method: 'GET' })
  }

  /**
   * 按分类获取资源
   * @param {string} category 分类
   * @param {Object} params 其他参数
   * @returns {Promise<Array>} 分类资源列表
   */
  async getByCategory(category, params = {}) {
    const queryParams = {
      category: category,
      ...params
    }
    
    return this.getList(queryParams)
  }

  /**
   * 获取热门资源
   * @param {Object} params 查询参数
   * @returns {Promise<Array>} 热门资源列表
   */
  async getPopular(params = {}) {
    const endpoint = `/${this.resourceName}/popular`
    const queryString = this.buildQueryString(params)
    return this.request(`${endpoint}${queryString}`, { method: 'GET' })
  }

  /**
   * 获取最新资源
   * @param {Object} params 查询参数
   * @returns {Promise<Array>} 最新资源列表
   */
  async getLatest(params = {}) {
    const defaultParams = {
      sort: 'created_at',
      order: 'desc',
      limit: 10,
      ...params
    }
    
    return this.getList(defaultParams)
  }

  // ===== 批量操作 =====

  /**
   * 批量获取资源
   * @param {Array<string|number>} ids ID列表
   * @returns {Promise<Array>} 资源列表
   */
  async getBatch(ids) {
    if (!ids || !Array.isArray(ids) || ids.length === 0) {
      throw new Error('ID列表不能为空')
    }
    
    const endpoint = `/${this.resourceName}/batch`
    return this.request(endpoint, {
      method: 'POST',
      data: { ids }
    })
  }

  /**
   * 批量删除资源
   * @param {Array<string|number>} ids ID列表
   * @returns {Promise<Object>} 删除结果
   */
  async deleteBatch(ids) {
    if (!ids || !Array.isArray(ids) || ids.length === 0) {
      throw new Error('ID列表不能为空')
    }
    
    const endpoint = `/${this.resourceName}/batch`
    return this.request(endpoint, {
      method: 'DELETE',
      data: { ids }
    })
  }

  // ===== 数据处理工具 =====

  /**
   * 构建查询字符串
   * @param {Object} params 查询参数
   * @returns {string} 查询字符串
   */
  buildQueryString(params) {
    if (!params || typeof params !== 'object') return ''
    
    const filteredParams = Object.entries(params)
      .filter(([key, value]) => value !== null && value !== undefined && value !== '')
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    
    return filteredParams.length > 0 ? `?${filteredParams.join('&')}` : ''
  }

  /**
   * 处理响应数据
   * @param {*} data 原始响应数据
   * @param {Function} transformer 数据转换函数
   * @returns {*} 处理后的数据
   */
  processResponse(data, transformer = null) {
    if (typeof transformer === 'function') {
      return transformer(data)
    }
    return data
  }

  /**
   * 缓存数据
   * @param {string} key 缓存键
   * @param {*} data 数据
   * @param {number} ttl 过期时间(毫秒)
   */
  setCache(key, data, ttl = 5 * 60 * 1000) {
    const cacheData = {
      data: data,
      timestamp: Date.now(),
      ttl: ttl
    }
    
    try {
      wx.setStorageSync(`cache_${key}`, cacheData)
    } catch (error) {
      console.warn(`[${this.constructor.name}] 缓存失败:`, error)
    }
  }

  /**
   * 获取缓存数据
   * @param {string} key 缓存键
   * @returns {*} 缓存数据，过期或不存在则返回null
   */
  getCache(key) {
    try {
      const cacheData = wx.getStorageSync(`cache_${key}`)
      if (!cacheData) return null
      
      const { data, timestamp, ttl } = cacheData
      const isExpired = Date.now() - timestamp > ttl
      
      if (isExpired) {
        wx.removeStorageSync(`cache_${key}`)
        return null
      }
      
      return data
    } catch (error) {
      console.warn(`[${this.constructor.name}] 获取缓存失败:`, error)
      return null
    }
  }

  /**
   * 清除指定缓存
   * @param {string} key 缓存键
   */
  clearCache(key) {
    try {
      wx.removeStorageSync(`cache_${key}`)
    } catch (error) {
      console.warn(`[${this.constructor.name}] 清除缓存失败:`, error)
    }
  }

  /**
   * 清除所有相关缓存
   */
  clearAllCache() {
    try {
      const { keys } = wx.getStorageInfoSync()
      const cacheKeys = keys.filter(key => key.startsWith(`cache_${this.resourceName}_`))
      
      cacheKeys.forEach(key => {
        wx.removeStorageSync(key)
      })
    } catch (error) {
      console.warn(`[${this.constructor.name}] 清除所有缓存失败:`, error)
    }
  }

  // ===== 扩展点：子类可以重写 =====

  /**
   * 请求前处理 - 子类可以重写
   * @param {string} url 请求URL
   * @param {Object} options 请求选项
   * @returns {Object} 处理后的选项
   */
  beforeRequest(url, options) {
    return options
  }

  /**
   * 响应后处理 - 子类可以重写
   * @param {*} data 响应数据
   * @param {string} url 请求URL
   * @returns {*} 处理后的数据
   */
  afterResponse(data, url) {
    return data
  }

  /**
   * 错误处理 - 子类可以重写
   * @param {Error} error 错误对象
   * @param {string} url 请求URL
   */
  handleError(error, url) {
    console.error(`[${this.constructor.name}] API错误:`, error.message, url)
  }
}

module.exports = ResourceClient 