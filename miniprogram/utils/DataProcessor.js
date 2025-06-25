/**
 * 数据处理工具类
 * 统一处理数据格式化、转换、过滤、验证等操作
 * 消除各页面中重复的数据处理逻辑
 */
class DataProcessor {
  
  // ===== 日期时间格式化 =====
  
  /**
   * 格式化日期
   * @param {string|Date} dateString 日期字符串或Date对象
   * @param {string} format 格式模式 YYYY-MM-DD HH:mm:ss
   * @returns {string} 格式化后的日期字符串
   */
  static formatDate(dateString, format = 'YYYY-MM-DD') {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return dateString
    
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    
    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hours)
      .replace('mm', minutes)
      .replace('ss', seconds)
  }

  /**
   * 格式化相对时间
   * @param {string|Date} dateString 日期字符串
   * @returns {string} 相对时间描述
   */
  static formatRelativeTime(dateString) {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    
    const minutes = Math.floor(diffMs / (1000 * 60))
    const hours = Math.floor(diffMs / (1000 * 60 * 60))
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    
    return this.formatDate(dateString, 'MM-DD')
  }

  /**
   * 格式化学期显示
   * @param {string} semester 学期代码 如：2024-2025-1
   * @returns {string} 格式化后的学期
   */
  static formatSemester(semester) {
    if (!semester) return ''
    
    const parts = semester.split('-')
    if (parts.length === 3) {
      const startYear = parts[0]
      const endYear = parts[1]
      const semesterNum = parts[2]
      const semesterName = semesterNum === '1' ? '第一学期' : '第二学期'
      return `${startYear}-${endYear}学年 ${semesterName}`
    }
    
    return semester
  }

  // ===== 数字和金额格式化 =====

  /**
   * 格式化金额
   * @param {number|string} amount 金额
   * @param {string} prefix 前缀符号
   * @param {number} decimals 小数位数
   * @returns {string} 格式化后的金额
   */
  static formatAmount(amount, prefix = '', decimals = 2) {
    if (amount === null || amount === undefined) return `${prefix}0.00`
    
    const num = parseFloat(amount)
    if (isNaN(num)) return `${prefix}0.00`
    
    return `${prefix}${num.toFixed(decimals)}`
  }

  /**
   * 格式化百分比
   * @param {number} value 数值
   * @param {number} decimals 小数位数
   * @returns {string} 百分比字符串
   */
  static formatPercentage(value, decimals = 1) {
    if (value === null || value === undefined) return '0%'
    
    const num = parseFloat(value)
    if (isNaN(num)) return '0%'
    
    return `${num.toFixed(decimals)}%`
  }

  /**
   * 格式化成绩等级
   * @param {number} score 分数
   * @returns {string} 等级字母
   */
  static formatGradeLevel(score) {
    if (score === null || score === undefined) return 'N/A'
    
    const num = parseFloat(score)
    if (isNaN(num)) return 'N/A'
    
    if (num >= 90) return 'A'
    if (num >= 80) return 'B'
    if (num >= 70) return 'C'
    if (num >= 60) return 'D'
    return 'F'
  }

  // ===== 数据转换 =====

  /**
   * 映射分类
   * @param {string} apiCategory API返回的分类
   * @param {Object} categoryMap 分类映射表
   * @returns {string} 映射后的分类
   */
  static mapCategory(apiCategory, categoryMap = {}) {
    return categoryMap[apiCategory] || 'other'
  }

  /**
   * 映射公告分类
   * @param {string} apiCategory API分类
   * @returns {string} 前端分类
   */
  static mapAnnouncementCategory(apiCategory) {
    const categoryMap = {
      'education': 'academic',
      'academic': 'academic',
      'student_affairs': 'student',
      'student': 'student',
      'logistics': 'logistics',
      'system': 'logistics',
      'sports': 'student',
      'general': 'academic',
      'administration': 'academic'
    }
    return this.mapCategory(apiCategory, categoryMap)
  }

  /**
   * 映射交易分类
   * @param {string} apiCategory API分类
   * @param {string} merchantName 商户名称
   * @returns {string} 前端分类
   */
  static mapTransactionCategory(apiCategory, merchantName = '') {
    const categoryMap = {
      '餐饮': 'dining',
      '购物': 'shopping',
      '图书馆': 'library',
      '其他': 'other'
    }
    
    // 如果API返回了分类，使用映射
    if (apiCategory && categoryMap[apiCategory]) {
      return categoryMap[apiCategory]
    }
    
    // 根据商户名称推断分类
    if (merchantName) {
      if (merchantName.includes('食堂') || merchantName.includes('餐厅')) {
        return 'dining'
      } else if (merchantName.includes('超市') || merchantName.includes('商店')) {
        return 'shopping'
      } else if (merchantName.includes('图书馆') || merchantName.includes('打印')) {
        return 'library'
      } else if (merchantName.includes('咖啡') || merchantName.includes('茶')) {
        return 'coffee'
      }
    }
    
    return 'other'
  }

  /**
   * 处理API响应数据
   * @param {Object} response API响应
   * @returns {Object} 处理后的数据
   */
  static processAPIResponse(response) {
    if (!response) return null
    
    // 统一的响应结构处理
    if (response.code === 0) {
      return response.data
    } else {
      throw new Error(response.message || 'API请求失败')
    }
  }

  /**
   * 标准化数据格式
   * @param {Object} data 原始数据
   * @param {Object} schema 数据模式
   * @returns {Object} 标准化后的数据
   */
  static normalizeData(data, schema = {}) {
    if (!data || typeof data !== 'object') return data
    
    const normalized = {}
    
    for (const [key, value] of Object.entries(data)) {
      const fieldSchema = schema[key]
      
      if (fieldSchema) {
        // 根据schema进行类型转换
        switch (fieldSchema.type) {
          case 'date':
            normalized[key] = this.formatDate(value, fieldSchema.format)
            break
          case 'amount':
            normalized[key] = this.formatAmount(value, fieldSchema.prefix, fieldSchema.decimals)
            break
          case 'category':
            normalized[key] = this.mapCategory(value, fieldSchema.map)
            break
          default:
            normalized[key] = value
        }
      } else {
        normalized[key] = value
      }
    }
    
    return normalized
  }

  // ===== 数据过滤 =====

  /**
   * 按关键词过滤
   * @param {Array} dataList 数据列表
   * @param {string} keyword 关键词
   * @param {Array} searchFields 搜索字段
   * @returns {Array} 过滤后的数据
   */
  static filterByKeyword(dataList, keyword, searchFields = ['title', 'content']) {
    if (!dataList || !Array.isArray(dataList)) return []
    if (!keyword || !keyword.trim()) return dataList
    
    const lowerKeyword = keyword.toLowerCase().trim()
    
    return dataList.filter(item => 
      searchFields.some(field => {
        const value = item[field]
        return value && String(value).toLowerCase().includes(lowerKeyword)
      })
    )
  }

  /**
   * 按分类过滤
   * @param {Array} dataList 数据列表
   * @param {string} category 分类
   * @param {string} categoryField 分类字段名
   * @returns {Array} 过滤后的数据
   */
  static filterByCategory(dataList, category, categoryField = 'category') {
    if (!dataList || !Array.isArray(dataList)) return []
    if (!category || category === 'all') return dataList
    
    return dataList.filter(item => item[categoryField] === category)
  }

  /**
   * 按日期范围过滤
   * @param {Array} dataList 数据列表
   * @param {string} startDate 开始日期
   * @param {string} endDate 结束日期
   * @param {string} dateField 日期字段名
   * @returns {Array} 过滤后的数据
   */
  static filterByDateRange(dataList, startDate, endDate, dateField = 'date') {
    if (!dataList || !Array.isArray(dataList)) return []
    
    return dataList.filter(item => {
      const itemDate = new Date(item[dateField])
      if (isNaN(itemDate.getTime())) return true
      
      if (startDate) {
        const start = new Date(startDate)
        if (itemDate < start) return false
      }
      
      if (endDate) {
        const end = new Date(endDate)
        if (itemDate > end) return false
      }
      
      return true
    })
  }

  /**
   * 多条件组合过滤
   * @param {Array} dataList 数据列表
   * @param {Object} filters 过滤条件
   * @returns {Array} 过滤后的数据
   */
  static filterByMultipleConditions(dataList, filters = {}) {
    if (!dataList || !Array.isArray(dataList)) return []
    
    let filtered = [...dataList]
    
    // 关键词过滤
    if (filters.keyword) {
      filtered = this.filterByKeyword(filtered, filters.keyword, filters.searchFields)
    }
    
    // 分类过滤
    if (filters.category) {
      filtered = this.filterByCategory(filtered, filters.category, filters.categoryField)
    }
    
    // 日期范围过滤
    if (filters.startDate || filters.endDate) {
      filtered = this.filterByDateRange(filtered, filters.startDate, filters.endDate, filters.dateField)
    }
    
    // 自定义过滤条件
    if (filters.custom && typeof filters.custom === 'function') {
      filtered = filtered.filter(filters.custom)
    }
    
    return filtered
  }

  // ===== 数据排序 =====

  /**
   * 按时间排序
   * @param {Array} dataList 数据列表
   * @param {string} dateField 日期字段
   * @param {string} order 排序方向 asc|desc
   * @returns {Array} 排序后的数据
   */
  static sortByTime(dataList, dateField = 'created_at', order = 'desc') {
    if (!dataList || !Array.isArray(dataList)) return []
    
    return [...dataList].sort((a, b) => {
      const dateA = new Date(a[dateField])
      const dateB = new Date(b[dateField])
      
      if (isNaN(dateA.getTime()) || isNaN(dateB.getTime())) return 0
      
      return order === 'desc' ? dateB - dateA : dateA - dateB
    })
  }

  /**
   * 按优先级排序
   * @param {Array} dataList 数据列表
   * @param {string} priorityField 优先级字段
   * @returns {Array} 排序后的数据
   */
  static sortByPriority(dataList, priorityField = 'priority') {
    if (!dataList || !Array.isArray(dataList)) return []
    
    const priorityOrder = { 'high': 3, 'medium': 2, 'normal': 1, 'low': 0 }
    
    return [...dataList].sort((a, b) => {
      const priorityA = priorityOrder[a[priorityField]] || 0
      const priorityB = priorityOrder[b[priorityField]] || 0
      return priorityB - priorityA
    })
  }

  /**
   * 按分数排序
   * @param {Array} dataList 数据列表
   * @param {string} scoreField 分数字段
   * @param {string} order 排序方向
   * @returns {Array} 排序后的数据
   */
  static sortByScore(dataList, scoreField = 'score', order = 'desc') {
    if (!dataList || !Array.isArray(dataList)) return []
    
    return [...dataList].sort((a, b) => {
      const scoreA = parseFloat(a[scoreField]) || 0
      const scoreB = parseFloat(b[scoreField]) || 0
      
      return order === 'desc' ? scoreB - scoreA : scoreA - scoreB
    })
  }

  // ===== 数据验证 =====

  /**
   * 验证必填字段
   * @param {Object} data 数据对象
   * @param {Array} requiredFields 必填字段列表
   * @returns {Object} 验证结果
   */
  static validateRequired(data, requiredFields) {
    const errors = []
    
    requiredFields.forEach(field => {
      if (!data[field] || (typeof data[field] === 'string' && !data[field].trim())) {
        errors.push(`${field} 是必填字段`)
      }
    })
    
    return {
      isValid: errors.length === 0,
      errors
    }
  }

  /**
   * 验证数据格式
   * @param {*} value 要验证的值
   * @param {string} type 数据类型
   * @returns {boolean} 是否有效
   */
  static validateFormat(value, type) {
    switch (type) {
      case 'email':
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
      case 'phone':
        return /^1[3-9]\d{9}$/.test(value)
      case 'number':
        return !isNaN(parseFloat(value)) && isFinite(value)
      case 'date':
        return !isNaN(Date.parse(value))
      default:
        return true
    }
  }

  /**
   * 验证数值范围
   * @param {number} value 数值
   * @param {number} min 最小值
   * @param {number} max 最大值
   * @returns {boolean} 是否在范围内
   */
  static validateRange(value, min = null, max = null) {
    const num = parseFloat(value)
    if (isNaN(num)) return false
    
    if (min !== null && num < min) return false
    if (max !== null && num > max) return false
    
    return true
  }

  // ===== 分页数据处理 =====

  /**
   * 处理分页数据
   * @param {Object} response API响应
   * @param {Array} currentData 当前数据
   * @param {boolean} isRefresh 是否刷新
   * @returns {Object} 处理后的分页数据
   */
  static processPaginatedData(response, currentData = [], isRefresh = false) {
    const data = this.processAPIResponse(response)
    
    if (!data) return { list: currentData, hasMore: false, total: 0 }
    
    const newList = data.list || data.records || data.data || []
    const total = data.total || 0
    const hasMore = data.hasMore !== undefined ? data.hasMore : newList.length > 0
    
    return {
      list: isRefresh ? newList : [...currentData, ...newList],
      hasMore,
      total
    }
  }
}

module.exports = DataProcessor 