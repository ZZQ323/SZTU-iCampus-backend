const ResourceClient = require('../ResourceClient')
const DataProcessor = require('../DataProcessor')

/**
 * 校园卡客户端
 * 处理校园卡相关的API操作
 * 包括余额查询、交易记录、消费分析、统计报表等
 */
class CampusCardClient extends ResourceClient {
  constructor() {
    super('http://localhost:8000', 'campus-card')
    this.cacheTimeout = 2 * 60 * 1000 // 2分钟缓存，校园卡数据需要较新
  }

  /**
   * 获取校园卡信息
   * @param {boolean} useCache 是否使用缓存
   * @returns {Promise<Object>} 校园卡信息
   */
  async getCardInfo(useCache = true) {
    const cacheKey = 'campus_card_info'
    
    if (useCache) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        console.log('[CampusCardClient] 📦 使用缓存的卡片信息')
        return cached
      }
    }

    try {
      const response = await this.request('/campus-card/info', {
        method: 'GET'
      })
      
      const processedInfo = this.processCardInfo(response)
      
      // 设置缓存
      this.setCache(cacheKey, processedInfo, this.cacheTimeout)
      
      return processedInfo
    } catch (error) {
      console.error('[CampusCardClient] 获取校园卡信息失败:', error)
      throw error
    }
  }

  /**
   * 获取交易记录
   * @param {Object} params 查询参数
   * @param {boolean} useCache 是否使用缓存
   * @returns {Promise<Array>} 交易记录列表
   */
  async getTransactions(params = {}, useCache = true) {
    const cacheKey = `transactions_${JSON.stringify(params)}`
    
    if (useCache) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        console.log('[CampusCardClient] 📦 使用缓存的交易记录')
        return cached
      }
    }

    try {
      const response = await this.request('/campus-card/transactions', {
        method: 'GET',
        data: params
      })
      
      const processedTransactions = this.processTransactionList(response)
      
      // 交易记录缓存时间较短
      this.setCache(cacheKey, processedTransactions, this.cacheTimeout)
      
      return processedTransactions
    } catch (error) {
      console.error('[CampusCardClient] 获取交易记录失败:', error)
      throw error
    }
  }

  /**
   * 获取消费统计
   * @param {string} period 统计周期：day|week|month|year
   * @param {string} startDate 开始日期
   * @param {string} endDate 结束日期
   * @returns {Promise<Object>} 消费统计
   */
  async getSpendingStatistics(period = 'month', startDate = null, endDate = null) {
    const cacheKey = `spending_stats_${period}_${startDate}_${endDate}`
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const params = { period }
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
      
      const response = await this.request('/campus-card/statistics', {
        method: 'GET',
        data: params
      })
      
      const processedStats = this.processSpendingStatistics(response)
      
      // 统计数据缓存时间较长
      this.setCache(cacheKey, processedStats, 15 * 60 * 1000)
      
      return processedStats
    } catch (error) {
      console.error('[CampusCardClient] 获取消费统计失败:', error)
      return this.getDefaultStatistics()
    }
  }

  /**
   * 获取月度消费分析
   * @param {string} month 月份，格式：YYYY-MM
   * @returns {Promise<Object>} 月度分析数据
   */
  async getMonthlyAnalysis(month = null) {
    const currentMonth = month || DataProcessor.formatDate(new Date(), 'YYYY-MM')
    const cacheKey = `monthly_analysis_${currentMonth}`
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request('/campus-card/monthly-analysis', {
        method: 'GET',
        data: { month: currentMonth }
      })
      
      const processedAnalysis = this.processMonthlyAnalysis(response)
      
      this.setCache(cacheKey, processedAnalysis, 30 * 60 * 1000)
      
      return processedAnalysis
    } catch (error) {
      console.error('[CampusCardClient] 获取月度分析失败:', error)
      return this.getDefaultMonthlyAnalysis()
    }
  }

  /**
   * 获取消费趋势
   * @param {number} days 天数
   * @returns {Promise<Object>} 趋势数据
   */
  async getSpendingTrends(days = 30) {
    const cacheKey = `spending_trends_${days}`
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request('/campus-card/trends', {
        method: 'GET',
        data: { days }
      })
      
      const processedTrends = this.processSpendingTrends(response)
      
      this.setCache(cacheKey, processedTrends, 20 * 60 * 1000)
      
      return processedTrends
    } catch (error) {
      console.error('[CampusCardClient] 获取消费趋势失败:', error)
      return {
        dailySpending: [],
        categoryTrends: {},
        averageDailySpending: 0
      }
    }
  }

  /**
   * 获取充值记录
   * @param {Object} params 查询参数
   * @returns {Promise<Array>} 充值记录列表
   */
  async getRechargeHistory(params = {}) {
    try {
      const response = await this.request('/campus-card/recharge-history', {
        method: 'GET',
        data: params
      })
      
      return this.processRechargeList(response)
    } catch (error) {
      console.error('[CampusCardClient] 获取充值记录失败:', error)
      throw error
    }
  }

  /**
   * 处理校园卡信息
   * @param {Object} data 原始卡片信息
   * @returns {Object} 处理后的卡片信息
   */
  processCardInfo(data) {
    if (!data || typeof data !== 'object') {
      return this.getDefaultCardInfo()
    }

    return {
      cardNumber: data.card_number || data.cardNumber || '未知',
      balance: DataProcessor.formatAmount(data.balance, '¥'),
      frozenAmount: DataProcessor.formatAmount(data.frozen_amount || 0, '¥'),
      availableBalance: DataProcessor.formatAmount(
        (data.balance || 0) - (data.frozen_amount || 0), '¥'
      ),
      lastTransactionTime: data.last_transaction_time 
        ? DataProcessor.formatDate(data.last_transaction_time, 'YYYY-MM-DD HH:mm')
        : '无交易记录',
      status: data.status || 'active',
      statusText: this.getCardStatusText(data.status),
      
      // 统计信息
      todaySpending: DataProcessor.formatAmount(data.today_spending || 0, '¥'),
      monthlySpending: DataProcessor.formatAmount(data.monthly_spending || 0, '¥'),
      totalRecharge: DataProcessor.formatAmount(data.total_recharge || 0, '¥'),
      
      raw: data
    }
  }

  /**
   * 处理交易记录列表
   * @param {Array|Object} data 原始交易数据
   * @returns {Array} 处理后的交易记录
   */
  processTransactionList(data) {
    let transactions = []
    
    if (Array.isArray(data)) {
      transactions = data
    } else if (data && data.list) {
      transactions = data.list
    } else if (data && data.transactions) {
      transactions = data.transactions
    } else {
      return []
    }

    return transactions.map(item => this.processTransactionItem(item))
  }

  /**
   * 处理单条交易记录
   * @param {Object} item 原始交易数据
   * @returns {Object} 处理后的交易数据
   */
  processTransactionItem(item) {
    if (!item || typeof item !== 'object') {
      return item
    }

    const amount = parseFloat(item.amount || 0)
    const isIncome = amount > 0

    return {
      id: item.id,
      transactionId: item.transaction_id || item.id,
      amount: Math.abs(amount),
      amountText: DataProcessor.formatAmount(Math.abs(amount), '¥'),
      type: isIncome ? 'income' : 'expense',
      typeText: isIncome ? '收入' : '支出',
      category: DataProcessor.mapTransactionCategory(item.category, item.merchant_name),
      categoryText: this.getCategoryText(item.category, item.merchant_name),
      merchantName: item.merchant_name || item.merchant || '未知商户',
      location: item.location || '',
      transactionTime: DataProcessor.formatDate(item.transaction_time || item.created_at, 'YYYY-MM-DD HH:mm'),
      relativeTime: DataProcessor.formatRelativeTime(item.transaction_time || item.created_at),
      balanceAfter: DataProcessor.formatAmount(item.balance_after || 0, '¥'),
      
      // 状态信息
      status: item.status || 'success',
      statusText: this.getTransactionStatusText(item.status),
      
      raw: item
    }
  }

  /**
   * 处理消费统计数据
   * @param {Object} data 原始统计数据
   * @returns {Object} 处理后的统计数据
   */
  processSpendingStatistics(data) {
    return {
      totalSpending: DataProcessor.formatAmount(data.total_spending || 0, '¥'),
      totalIncome: DataProcessor.formatAmount(data.total_income || 0, '¥'),
      transactionCount: data.transaction_count || 0,
      averageTransaction: DataProcessor.formatAmount(data.average_transaction || 0, '¥'),
      
      // 分类统计
      categoryBreakdown: this.processCategoryBreakdown(data.category_breakdown || {}),
      
      // 时间统计
      dailyAverage: DataProcessor.formatAmount(data.daily_average || 0, '¥'),
      weeklyAverage: DataProcessor.formatAmount(data.weekly_average || 0, '¥'),
      monthlyAverage: DataProcessor.formatAmount(data.monthly_average || 0, '¥'),
      
      // 商户统计
      topMerchants: (data.top_merchants || []).map(merchant => ({
        name: merchant.name,
        amount: DataProcessor.formatAmount(merchant.amount || 0, '¥'),
        count: merchant.count || 0
      }))
    }
  }

  /**
   * 处理月度分析数据
   * @param {Object} data 原始月度数据
   * @returns {Object} 处理后的月度分析
   */
  processMonthlyAnalysis(data) {
    return {
      month: data.month,
      monthName: this.getMonthName(data.month),
      totalSpending: DataProcessor.formatAmount(data.total_spending || 0, '¥'),
      dailyData: (data.daily_data || []).map(day => ({
        date: day.date,
        spending: parseFloat(day.spending || 0),
        transactionCount: day.transaction_count || 0
      })),
      
      // 对比数据
      comparison: {
        lastMonth: {
          spending: DataProcessor.formatAmount(data.last_month_spending || 0, '¥'),
          change: this.calculateChange(data.total_spending, data.last_month_spending),
          changeText: this.getChangeText(data.total_spending, data.last_month_spending)
        }
      },
      
      // 消费分布
      weekdayDistribution: data.weekday_distribution || {},
      timeDistribution: data.time_distribution || {},
      
      // 预测
      predictedSpending: DataProcessor.formatAmount(data.predicted_spending || 0, '¥')
    }
  }

  /**
   * 处理消费趋势数据
   * @param {Object} data 原始趋势数据
   * @returns {Object} 处理后的趋势数据
   */
  processSpendingTrends(data) {
    return {
      dailySpending: (data.daily_spending || []).map(item => ({
        date: item.date,
        spending: parseFloat(item.spending || 0),
        transactionCount: item.transaction_count || 0
      })),
      
      categoryTrends: data.category_trends || {},
      
      averageDailySpending: parseFloat(data.average_daily_spending || 0),
      
      // 趋势分析
      trend: data.trend || 'stable', // increasing, decreasing, stable
      trendText: this.getTrendText(data.trend),
      
      // 周期性分析
      weeklyPattern: data.weekly_pattern || {},
      monthlyPattern: data.monthly_pattern || {}
    }
  }

  /**
   * 处理充值记录列表
   * @param {Array|Object} data 原始充值数据
   * @returns {Array} 处理后的充值记录
   */
  processRechargeList(data) {
    let recharges = []
    
    if (Array.isArray(data)) {
      recharges = data
    } else if (data && data.list) {
      recharges = data.list
    } else {
      return []
    }

    return recharges.map(item => ({
      id: item.id,
      amount: DataProcessor.formatAmount(item.amount || 0, '¥'),
      method: item.method || 'unknown',
      methodText: this.getRechargeMethodText(item.method),
      rechargeTime: DataProcessor.formatDate(item.recharge_time || item.created_at, 'YYYY-MM-DD HH:mm'),
      status: item.status || 'success',
      statusText: this.getRechargeStatusText(item.status),
      transactionId: item.transaction_id || item.id,
      raw: item
    }))
  }

  /**
   * 处理分类统计
   * @param {Object} breakdown 分类统计数据
   * @returns {Object} 处理后的分类统计
   */
  processCategoryBreakdown(breakdown) {
    const processed = {}
    
    Object.entries(breakdown).forEach(([category, data]) => {
      processed[category] = {
        amount: DataProcessor.formatAmount(data.amount || 0, '¥'),
        count: data.count || 0,
        percentage: data.percentage ? `${data.percentage.toFixed(1)}%` : '0%',
        categoryText: this.getCategoryText(category)
      }
    })
    
    return processed
  }

  /**
   * 获取卡片状态文本
   * @param {string} status 状态代码
   * @returns {string} 状态文本
   */
  getCardStatusText(status) {
    const statusMap = {
      'active': '正常',
      'frozen': '冻结',
      'lost': '挂失',
      'expired': '过期',
      'inactive': '未激活'
    }
    return statusMap[status] || '未知'
  }

  /**
   * 获取交易状态文本
   * @param {string} status 状态代码
   * @returns {string} 状态文本
   */
  getTransactionStatusText(status) {
    const statusMap = {
      'success': '成功',
      'pending': '处理中',
      'failed': '失败',
      'cancelled': '已取消'
    }
    return statusMap[status] || '未知'
  }

  /**
   * 获取分类文本
   * @param {string} category 分类代码
   * @param {string} merchantName 商户名称
   * @returns {string} 分类文本
   */
  getCategoryText(category, merchantName = '') {
    const categoryMap = {
      'dining': '餐饮',
      'shopping': '购物',
      'library': '图书馆',
      'coffee': '咖啡茶饮',
      'other': '其他'
    }
    
    return categoryMap[category] || '其他'
  }

  /**
   * 获取充值方式文本
   * @param {string} method 充值方式
   * @returns {string} 方式文本
   */
  getRechargeMethodText(method) {
    const methodMap = {
      'alipay': '支付宝',
      'wechat': '微信支付',
      'bank': '银行卡',
      'cash': '现金',
      'online': '网上银行'
    }
    return methodMap[method] || '未知'
  }

  /**
   * 获取充值状态文本
   * @param {string} status 状态代码
   * @returns {string} 状态文本
   */
  getRechargeStatusText(status) {
    const statusMap = {
      'success': '成功',
      'pending': '处理中',
      'failed': '失败',
      'cancelled': '已取消'
    }
    return statusMap[status] || '未知'
  }

  /**
   * 计算变化百分比
   * @param {number} current 当前值
   * @param {number} previous 之前值
   * @returns {number} 变化百分比
   */
  calculateChange(current, previous) {
    if (!previous || previous === 0) return 0
    return ((current - previous) / previous * 100)
  }

  /**
   * 获取变化文本
   * @param {number} current 当前值
   * @param {number} previous 之前值
   * @returns {string} 变化文本
   */
  getChangeText(current, previous) {
    const change = this.calculateChange(current, previous)
    if (change > 0) {
      return `较上月增加 ${change.toFixed(1)}%`
    } else if (change < 0) {
      return `较上月减少 ${Math.abs(change).toFixed(1)}%`
    } else {
      return '与上月持平'
    }
  }

  /**
   * 获取趋势文本
   * @param {string} trend 趋势代码
   * @returns {string} 趋势文本
   */
  getTrendText(trend) {
    const trendMap = {
      'increasing': '支出增长',
      'decreasing': '支出下降',
      'stable': '支出稳定'
    }
    return trendMap[trend] || '无趋势'
  }

  /**
   * 获取月份名称
   * @param {string} month 月份，格式：YYYY-MM
   * @returns {string} 月份名称
   */
  getMonthName(month) {
    if (!month) return ''
    const [year, monthNum] = month.split('-')
    return `${year}年${parseInt(monthNum)}月`
  }

  /**
   * 获取默认卡片信息
   * @returns {Object} 默认卡片信息
   */
  getDefaultCardInfo() {
    return {
      cardNumber: '未知',
      balance: '¥0.00',
      frozenAmount: '¥0.00',
      availableBalance: '¥0.00',
      lastTransactionTime: '无交易记录',
      status: 'unknown',
      statusText: '未知',
      todaySpending: '¥0.00',
      monthlySpending: '¥0.00',
      totalRecharge: '¥0.00'
    }
  }

  /**
   * 获取默认统计信息
   * @returns {Object} 默认统计
   */
  getDefaultStatistics() {
    return {
      totalSpending: '¥0.00',
      totalIncome: '¥0.00',
      transactionCount: 0,
      averageTransaction: '¥0.00',
      categoryBreakdown: {},
      dailyAverage: '¥0.00',
      weeklyAverage: '¥0.00',
      monthlyAverage: '¥0.00',
      topMerchants: []
    }
  }

  /**
   * 获取默认月度分析
   * @returns {Object} 默认月度分析
   */
  getDefaultMonthlyAnalysis() {
    return {
      month: DataProcessor.formatDate(new Date(), 'YYYY-MM'),
      monthName: this.getMonthName(DataProcessor.formatDate(new Date(), 'YYYY-MM')),
      totalSpending: '¥0.00',
      dailyData: [],
      comparison: {
        lastMonth: {
          spending: '¥0.00',
          change: 0,
          changeText: '无数据对比'
        }
      },
      weekdayDistribution: {},
      timeDistribution: {},
      predictedSpending: '¥0.00'
    }
  }

  /**
   * 错误处理
   * @param {Error} error 错误对象
   * @param {string} url 请求URL
   */
  handleError(error, url) {
    console.error(`[CampusCardClient] ❌ 请求失败:`, url, error.message)
    
    if (error.message.includes('401')) {
      throw new Error('登录已过期，请重新登录后查看校园卡信息')
    } else if (error.message.includes('403')) {
      throw new Error('暂无权限查看校园卡信息')
    } else if (error.message.includes('网络')) {
      throw new Error('网络连接失败，请检查网络设置')
    } else {
      throw error
    }
  }
}

module.exports = CampusCardClient 