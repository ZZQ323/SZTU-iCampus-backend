const ResourceClient = require('../ResourceClient')
const DataProcessor = require('../DataProcessor')

/**
 * 公告客户端
 * 处理公告相关的API操作
 * 包括列表获取、搜索、分类过滤、热门公告等
 */
class AnnouncementClient extends ResourceClient {
  constructor() {
    super('http://localhost:8000', 'announcements')
    this.cacheTimeout = 5 * 60 * 1000 // 5分钟缓存
  }

  /**
   * 获取公告列表（带缓存）
   * @param {Object} params 查询参数
   * @param {boolean} useCache 是否使用缓存
   * @returns {Promise<Array>} 公告列表
   */
  async getAnnouncements(params = {}, useCache = true) {
    const cacheKey = `announcements_${JSON.stringify(params)}`
    
    if (useCache) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        console.log('[AnnouncementClient] 📦 使用缓存数据')
        return cached
      }
    }

    try {
      const data = await this.getList(params)
      
      // 处理数据格式
      const processedData = this.processAnnouncementList(data)
      
      // 设置缓存
      this.setCache(cacheKey, processedData, this.cacheTimeout)
      
      return processedData
    } catch (error) {
      console.error('[AnnouncementClient] 获取公告列表失败:', error)
      throw error
    }
  }

  /**
   * 搜索公告
   * @param {string} keyword 搜索关键词
   * @param {Object} filters 过滤条件
   * @returns {Promise<Array>} 搜索结果
   */
  async searchAnnouncements(keyword, filters = {}) {
    try {
      const params = {
        search: keyword,
        q: keyword,
        keyword: keyword,
        ...filters
      }
      
      const response = await this.request('/announcements/search', {
        method: 'GET',
        data: params
      })
      
      return this.processAnnouncementList(response)
    } catch (error) {
      console.error('[AnnouncementClient] 搜索公告失败:', error)
      throw error
    }
  }

  /**
   * 按分类获取公告
   * @param {string} category 分类
   * @param {Object} params 其他参数
   * @returns {Promise<Array>} 分类公告列表
   */
  async getByCategory(category, params = {}) {
    try {
      const queryParams = {
        category: category,
        ...params
      }
      
      const data = await this.getList(queryParams)
      return this.processAnnouncementList(data)
    } catch (error) {
      console.error('[AnnouncementClient] 获取分类公告失败:', error)
      throw error
    }
  }

  /**
   * 获取热门公告
   * @param {number} limit 数量限制
   * @returns {Promise<Array>} 热门公告列表
   */
  async getPopularAnnouncements(limit = 10) {
    const cacheKey = `popular_announcements_${limit}`
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request('/announcements/popular', {
        method: 'GET',
        data: { limit }
      })
      
      const processedData = this.processAnnouncementList(response)
      
      // 热门公告缓存时间更长
      this.setCache(cacheKey, processedData, 15 * 60 * 1000)
      
      return processedData
    } catch (error) {
      console.error('[AnnouncementClient] 获取热门公告失败:', error)
      throw error
    }
  }

  /**
   * 获取最新公告
   * @param {number} limit 数量限制
   * @returns {Promise<Array>} 最新公告列表
   */
  async getLatestAnnouncements(limit = 5) {
    try {
      const params = {
        sort: 'created_at',
        order: 'desc',
        limit: limit
      }
      
      const data = await this.getList(params)
      return this.processAnnouncementList(data)
    } catch (error) {
      console.error('[AnnouncementClient] 获取最新公告失败:', error)
      throw error
    }
  }

  /**
   * 获取公告详情
   * @param {string|number} id 公告ID
   * @returns {Promise<Object>} 公告详情
   */
  async getAnnouncementDetail(id) {
    const cacheKey = `announcement_detail_${id}`
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const data = await this.getById(id)
      const processedData = this.processAnnouncementDetail(data)
      
      // 详情缓存时间较长
      this.setCache(cacheKey, processedData, 10 * 60 * 1000)
      
      return processedData
    } catch (error) {
      console.error('[AnnouncementClient] 获取公告详情失败:', error)
      throw error
    }
  }

  /**
   * 获取公告统计信息
   * @returns {Promise<Object>} 统计信息
   */
  async getStatistics() {
    const cacheKey = 'announcement_statistics'
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request('/announcements/stats', {
        method: 'GET'
      })
      
      // 统计信息缓存时间更长
      this.setCache(cacheKey, response, 30 * 60 * 1000)
      
      return response
    } catch (error) {
      console.error('[AnnouncementClient] 获取统计信息失败:', error)
      // 返回默认统计信息
      return {
        total: 0,
        categories: {},
        recent: 0
      }
    }
  }

  /**
   * 标记公告为已读
   * @param {string|number} id 公告ID
   * @returns {Promise<boolean>} 是否成功
   */
  async markAsRead(id) {
    try {
      await this.request(`/announcements/${id}/read`, {
        method: 'POST'
      })
      
      // 清除相关缓存
      this.clearCache(`announcement_detail_${id}`)
      
      return true
    } catch (error) {
      console.error('[AnnouncementClient] 标记已读失败:', error)
      return false
    }
  }

  /**
   * 处理公告列表数据
   * @param {Array|Object} data 原始数据
   * @returns {Array} 处理后的公告列表
   */
  processAnnouncementList(data) {
    let announcements = []
    
    if (Array.isArray(data)) {
      announcements = data
    } else if (data && data.list) {
      announcements = data.list
    } else if (data && data.announcements) {
      announcements = data.announcements
    } else {
      return []
    }

    return announcements.map(item => this.processAnnouncementItem(item))
  }

  /**
   * 处理单个公告数据
   * @param {Object} item 原始公告数据
   * @returns {Object} 处理后的公告数据
   */
  processAnnouncementItem(item) {
    if (!item || typeof item !== 'object') {
      return item
    }

    return {
      id: item.id,
      title: item.title || '无标题',
      content: item.content || '',
      summary: item.summary || this.generateSummary(item.content),
      category: DataProcessor.mapAnnouncementCategory(item.category),
      categoryName: this.getCategoryName(item.category),
      author: item.author || '系统管理员',
      department: item.department || '教务处',
      publishTime: DataProcessor.formatDate(item.publish_time || item.created_at, 'YYYY-MM-DD HH:mm'),
      relativeTime: DataProcessor.formatRelativeTime(item.publish_time || item.created_at),
      priority: item.priority || 'normal',
      isImportant: item.is_important || item.priority === 'high',
      isRead: item.is_read || false,
      readCount: item.read_count || 0,
      attachments: item.attachments || [],
      tags: item.tags || [],
      
      // 原始数据保留
      raw: item
    }
  }

  /**
   * 处理公告详情数据
   * @param {Object} data 原始详情数据
   * @returns {Object} 处理后的详情数据
   */
  processAnnouncementDetail(data) {
    const processed = this.processAnnouncementItem(data)
    
    // 详情页面需要更多信息
    return {
      ...processed,
      fullContent: data.content || '',
      html: data.html || '',
      wordCount: data.content ? data.content.length : 0,
      readTime: this.estimateReadTime(data.content),
      relatedAnnouncements: (data.related || []).map(item => this.processAnnouncementItem(item))
    }
  }

  /**
   * 生成摘要
   * @param {string} content 内容
   * @param {number} maxLength 最大长度
   * @returns {string} 摘要
   */
  generateSummary(content, maxLength = 100) {
    if (!content || typeof content !== 'string') {
      return ''
    }
    
    const cleaned = content.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim()
    
    if (cleaned.length <= maxLength) {
      return cleaned
    }
    
    return cleaned.substring(0, maxLength) + '...'
  }

  /**
   * 估算阅读时间
   * @param {string} content 内容
   * @returns {string} 阅读时间
   */
  estimateReadTime(content) {
    if (!content) return '1分钟'
    
    const wordsPerMinute = 300 // 中文平均阅读速度
    const wordCount = content.length
    const minutes = Math.ceil(wordCount / wordsPerMinute)
    
    return `${minutes}分钟`
  }

  /**
   * 获取分类显示名称
   * @param {string} category 分类代码
   * @returns {string} 分类名称
   */
  getCategoryName(category) {
    const categoryNames = {
      'academic': '教务公告',
      'student': '学生事务',
      'logistics': '后勤服务',
      'activity': '活动通知',
      'system': '系统通知',
      'other': '其他'
    }
    
    return categoryNames[category] || '其他'
  }

  /**
   * 响应后处理
   * @param {*} data 响应数据
   * @param {string} url 请求URL
   * @returns {*} 处理后的数据
   */
  afterResponse(data, url) {
    console.log(`[AnnouncementClient] 🔄 处理响应:`, url)
    return data
  }

  /**
   * 错误处理
   * @param {Error} error 错误对象
   * @param {string} url 请求URL
   */
  handleError(error, url) {
    console.error(`[AnnouncementClient] ❌ 请求失败:`, url, error.message)
    
    // 特定错误处理
    if (error.message.includes('网络')) {
      throw new Error('网络连接失败，请检查网络设置')
    } else if (error.message.includes('401')) {
      throw new Error('登录已过期，请重新登录')
    } else {
      throw error
    }
  }
}

module.exports = AnnouncementClient 