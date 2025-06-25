/**
 * 页面基类 - 所有页面的基础
 * 统一处理登录检查、API调用、错误处理、生命周期管理
 * 消除前端页面中80%的重复代码
 */
class BasePage {
  constructor() {
    this.data = {
      // 通用数据
      userInfo: null,
      isLoggedIn: false,
      loading: false,
      refreshing: false,
      error: null,
      
      // 合并子类的初始数据
      ...this.getInitialData()
    }
  }

  /**
   * 子类重写此方法提供特定的初始数据
   * @returns {Object} 页面特有的初始数据
   */
  getInitialData() {
    return {}
  }

  /**
   * 页面加载时 - 统一的生命周期管理
   */
  onLoad(options) {
    console.log(`[${this.getPageName()}] 📱 页面加载`)
    
    // 调用子类的beforeLoad钩子
    if (this.beforeLoad) {
      this.beforeLoad(options)
    }
    
    // 检查登录状态
    const isLoggedIn = this.checkLoginStatus()
    
    // 如果需要登录但未登录，则不继续加载
    if (this.requiresLogin() && !isLoggedIn) {
      return
    }
    
    // 加载初始数据
    this.loadInitialData(options).finally(() => {
      // 调用子类的afterLoad钩子
      if (this.afterLoad) {
        this.afterLoad(options)
      }
    })
  }

  /**
   * 页面显示时
   */
  onShow() {
    console.log(`[${this.getPageName()}] 👁️ 页面显示`)
    
    // 静默刷新数据
    this.refreshData(false)
  }

  /**
   * 页面隐藏时
   */
  onHide() {
    console.log(`[${this.getPageName()}] 🙈 页面隐藏`)
    
    // 清理定时器等资源
    this.cleanup()
  }

  /**
   * 页面卸载时
   */
  onUnload() {
    console.log(`[${this.getPageName()}] 🗑️ 页面卸载`)
    
    // 彻底清理资源
    this.cleanup()
  }

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    console.log(`[${this.getPageName()}] 🔄 下拉刷新`)
    
    this.setData({ refreshing: true })
    
    this.refreshData(true).finally(() => {
      wx.stopPullDownRefresh()
      this.setData({ refreshing: false })
      this.showToast('刷新完成', 'success')
    })
  }

  /**
   * 检查登录状态 - 统一的登录检查逻辑
   * @returns {boolean} 是否已登录
   */
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo
      })
      console.log(`[${this.getPageName()}] ✅ 用户已登录:`, userInfo.name)
      return true
    } else {
      this.setData({
        isLoggedIn: false,
        userInfo: null
      })
      
      if (this.requiresLogin()) {
        this.showLoginPrompt()
      }
      return false
    }
  }

  /**
   * 显示登录提示
   */
  showLoginPrompt() {
    wx.showModal({
      title: '需要登录',
      content: `访问${this.getPageName()}需要先登录，是否前往登录？`,
      success: (res) => {
        if (res.confirm) {
          this.navigate('/pages/login/login')
        } else {
          this.navigate('/pages/index/index', 'switchTab')
        }
      }
    })
  }

  /**
   * 统一的API调用包装器 - 消除重复的错误处理和loading状态
   * @param {Function} apiMethod API调用方法
   * @param {boolean} showLoading 是否显示loading
   * @param {string} errorMessage 自定义错误消息
   * @returns {Promise} API调用结果
   */
  async apiCall(apiMethod, showLoading = true, errorMessage = '操作失败') {
    if (showLoading) {
      this.setData({ loading: true })
    }
    
    try {
      const result = await apiMethod()
      this.setData({ error: null })
      return result
    } catch (error) {
      console.error(`[${this.getPageName()}] ❌ API调用失败:`, error)
      
      const message = error.message || errorMessage
      this.setData({ error: message })
      this.showToast(message, 'error')
      
      // 调用子类的错误处理钩子
      if (this.handleError) {
        this.handleError(error)
      }
      
      throw error
    } finally {
      if (showLoading) {
        this.setData({ loading: false })
      }
    }
  }

  /**
   * 统一的Toast提示
   * @param {string} title 提示内容
   * @param {string} type 提示类型：success|error|loading|none
   * @param {number} duration 显示时长
   */
  showToast(title, type = 'none', duration = 2000) {
    const iconMap = {
      success: 'success',
      error: 'error', 
      loading: 'loading',
      none: 'none'
    }
    
    wx.showToast({
      title,
      icon: iconMap[type] || 'none',
      duration
    })
  }

  /**
   * 统一的页面导航
   * @param {string} url 目标页面路径
   * @param {string} type 导航类型：navigateTo|redirectTo|switchTab|reLaunch
   */
  navigate(url, type = 'navigateTo') {
    const navigationMethods = {
      navigateTo: wx.navigateTo,
      redirectTo: wx.redirectTo,
      switchTab: wx.switchTab,
      reLaunch: wx.reLaunch
    }
    
    const method = navigationMethods[type] || wx.navigateTo
    
    method({
      url,
      fail: (error) => {
        console.error(`[${this.getPageName()}] 导航失败:`, error)
        this.showToast('页面跳转失败', 'error')
      }
    })
  }

  /**
   * 设置页面标题
   * @param {string} title 页面标题
   */
  setPageTitle(title) {
    wx.setNavigationBarTitle({
      title: title
    })
  }

  /**
   * 页面数据设置 - 封装setData以便扩展
   * @param {Object} data 要设置的数据
   * @param {Function} callback 回调函数
   */
  setData(data, callback) {
    if (this._page && this._page.setData) {
      this._page.setData(data, callback)
    }
  }

  /**
   * 绑定页面实例
   * @param {Object} page 页面实例
   */
  bindPage(page) {
    this._page = page
    page.data = { ...page.data, ...this.data }
  }

  /**
   * 资源清理 - 清理定时器、取消网络请求等
   */
  cleanup() {
    // 子类可以重写此方法进行特定的资源清理
  }

  // ===== 抽象方法：子类必须实现 =====

  /**
   * 获取页面名称 - 子类必须实现
   * @returns {string} 页面名称
   */
  getPageName() {
    throw new Error('子类必须实现 getPageName 方法')
  }

  /**
   * 加载初始数据 - 子类必须实现
   * @param {Object} options 页面参数
   * @returns {Promise} 加载Promise
   */
  async loadInitialData(options) {
    throw new Error('子类必须实现 loadInitialData 方法')
  }

  /**
   * 刷新数据 - 子类必须实现
   * @param {boolean} force 是否强制刷新
   * @returns {Promise} 刷新Promise
   */
  async refreshData(force = false) {
    throw new Error('子类必须实现 refreshData 方法')
  }

  // ===== 扩展点：子类可选实现 =====

  /**
   * 是否需要登录 - 子类可以重写
   * @returns {boolean} 是否需要登录
   */
  requiresLogin() {
    return true
  }

  /**
   * 页面加载前处理 - 子类可以重写
   * @param {Object} options 页面参数
   */
  beforeLoad(options) {
    // 子类可选实现
  }

  /**
   * 页面加载后处理 - 子类可以重写
   * @param {Object} options 页面参数
   */
  afterLoad(options) {
    // 子类可选实现
  }

  /**
   * 自定义错误处理 - 子类可以重写
   * @param {Error} error 错误对象
   */
  handleError(error) {
    // 子类可选实现
  }
}

/**
 * 页面混入工具 - 将BasePage的功能混入到小程序页面中
 * @param {BasePage} pageClass 页面类实例
 * @returns {Object} 小程序页面配置对象
 */
function createPage(pageClass) {
  const pageConfig = {
    data: pageClass.data,
    
    onLoad(options) {
      pageClass.bindPage(this)
      pageClass.onLoad(options)
    },
    
    onShow() {
      pageClass.onShow()
    },
    
    onHide() {
      pageClass.onHide()
    },
    
    onUnload() {
      pageClass.onUnload()
    },
    
    onPullDownRefresh() {
      pageClass.onPullDownRefresh()
    }
  }
  
  // 将页面类的方法复制到页面配置中
  const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(pageClass))
  methods.forEach(method => {
    if (method !== 'constructor' && typeof pageClass[method] === 'function') {
      // 如果页面配置中还没有这个方法，则添加
      if (!pageConfig[method]) {
        pageConfig[method] = pageClass[method].bind(pageClass)
      }
    }
  })
  
  return pageConfig
}

module.exports = {
  BasePage,
  createPage
} 