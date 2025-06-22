const app = getApp()

Page({
  data: {
    loginType: 'wechat', // wechat, password, guest
    formData: {
      loginId: '',
      password: '',
      name: ''
    },
    loading: false,
    wechatLoginStep: 'auth', // auth, bind
    wechatInfo: null,
    wechatCode: null
  },

  onLoad() {
    console.log('[登录] 页面加载')
    this.checkExistingLogin()
  },

  onShow() {
    // 检查是否需要显示微信授权
    this.checkWechatAuth()
  },

  // 检查是否已登录
  checkExistingLogin() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      wx.showModal({
        title: '已登录',
        content: `您已登录为 ${userInfo.name}，是否重新登录？`,
        success: (res) => {
          if (!res.confirm) {
            wx.navigateBack()
          }
        }
      })
    }
  },

  // 检查微信授权状态
  checkWechatAuth() {
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.userInfo']) {
          // 已授权，获取用户信息
          this.getWechatUserInfo()
        }
      }
    })
  },

  // 获取微信用户信息
  getWechatUserInfo() {
    wx.getUserInfo({
      success: (res) => {
        console.log('[微信] 获取用户信息成功', res)
        this.setData({
          wechatInfo: res.userInfo
        })
      },
      fail: (err) => {
        console.log('[微信] 获取用户信息失败', err)
      }
    })
  },

  // 切换登录类型
  onLoginTypeChange(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      loginType: type,
      formData: {
        loginId: '',
        password: '',
        name: ''
      },
      wechatLoginStep: 'auth'
    })
  },

  // 输入处理
  onLoginIdInput(e) {
    this.setData({
      'formData.loginId': e.detail.value
    })
  },

  onPasswordInput(e) {
    this.setData({
      'formData.password': e.detail.value
    })
  },

  onNameInput(e) {
    this.setData({
      'formData.name': e.detail.value
    })
  },

  // 微信登录
  async onWechatLogin() {
    this.setData({ loading: true })

    try {
      // 1. 获取微信登录凭证
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        })
      })

      if (!loginRes.code) {
        throw new Error('获取微信登录凭证失败')
      }

      console.log('[微信登录] 获取到code:', loginRes.code)
      this.setData({ wechatCode: loginRes.code })

      // 2. 检查是否已绑定账号
      const checkRes = await this.checkWechatBinding(loginRes.code)
      
      if (checkRes.is_bound) {
        // 已绑定，直接登录
        const loginResult = await this.loginWithWechatCode(loginRes.code)
        
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' })
        }, 1500)
      } else {
        // 未绑定，显示绑定界面
        this.setData({
          wechatLoginStep: 'bind'
        })
        wx.showToast({
          title: '请绑定校园账号',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('[微信登录] 失败', error)
      wx.showToast({
        title: error.message || '微信登录失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 检查微信绑定状态
  async checkWechatBinding(code) {
    try {
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseURL}/api/v1/auth/wechat/check-bind`,
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: { code: code },
          success: resolve,
          fail: reject
        })
      })

      console.log('[微信绑定检查] API响应', response)

      if (response.statusCode === 200) {
        return response.data
      } else {
        throw new Error(response.data?.msg || '检查绑定状态失败')
      }
    } catch (error) {
      console.error('[微信绑定检查] 失败', error)
      throw new Error('检查绑定状态失败')
    }
  },

  // 使用微信code登录
  async loginWithWechatCode(code) {
    try {
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseURL}/api/v1/auth/wechat/login`,
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: { 
            code: code,
            user_info: this.data.wechatInfo
          },
          success: resolve,
          fail: reject
        })
      })

      console.log('[微信登录] API响应', response)

      if (response.statusCode === 200) {
        const { access_token, user } = response.data
        
        // 保存登录信息
        wx.setStorageSync('token', access_token)
        wx.setStorageSync('userInfo', user)
        app.globalData.userInfo = user

        return response.data
      } else {
        throw new Error(response.data?.msg || '微信登录失败')
      }
    } catch (error) {
      console.error('[微信登录] API调用失败', error)
      throw error
    }
  },

  // 账号密码登录
  async onPasswordLogin() {
    const { formData } = this.data

    // 表单验证
    if (!formData.loginId) {
      wx.showToast({ title: '请输入学号/工号', icon: 'none' })
      return
    }
    if (!formData.password) {
      wx.showToast({ title: '请输入密码', icon: 'none' })
      return
    }

    this.setData({ loading: true })

    try {
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseURL}/api/v1/auth/login`,
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            login_id: formData.loginId,
            password: formData.password,
            remember_me: true
          },
          success: resolve,
          fail: reject
        })
      })

      console.log('[登录] API响应', response)

      if (response.statusCode === 200 && response.data.access_token) {
        const { access_token, user } = response.data
        
        // 保存登录信息
        wx.setStorageSync('token', access_token)
        wx.setStorageSync('userInfo', user)
        app.globalData.userInfo = user

        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })

        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' })
        }, 1500)
      } else {
        throw new Error(response.data?.msg || '登录失败')
      }
    } catch (error) {
      console.error('[登录] 失败', error)
      
      let errorMsg = '登录失败'
      if (error.statusCode === 401) {
        errorMsg = '用户名或密码错误'
      } else if (error.statusCode === 423) {
        errorMsg = '账户已被锁定'  
      } else if (error.data?.msg) {
        errorMsg = error.data.msg
      }

      wx.showToast({
        title: errorMsg,
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 绑定校园账号
  async onBindAccount() {
    const { formData, wechatCode } = this.data

    if (!formData.loginId || !formData.password) {
      wx.showToast({ title: '请输入完整的账号信息', icon: 'none' })
      return
    }

    if (!wechatCode) {
      wx.showToast({ title: '微信授权已过期，请重新操作', icon: 'none' })
      this.setData({ wechatLoginStep: 'auth' })
      return
    }

    this.setData({ loading: true })

    try {
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseURL}/api/v1/auth/wechat/bind`,
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            code: wechatCode,
            login_id: formData.loginId,
            password: formData.password,
            user_info: this.data.wechatInfo
          },
          success: resolve,
          fail: reject
        })
      })

      console.log('[微信绑定] API响应', response)

      if (response.statusCode === 200) {
        wx.showToast({
          title: '绑定成功',
          icon: 'success'
        })

        // 绑定成功后自动登录
        setTimeout(async () => {
          try {
            await this.loginWithWechatCode(wechatCode)
            wx.switchTab({ url: '/pages/index/index' })
          } catch (loginError) {
            console.error('[绑定后登录] 失败', loginError)
            wx.showToast({
              title: '绑定成功，请重新登录',
              icon: 'none'
            })
            this.setData({ wechatLoginStep: 'auth' })
          }
        }, 1500)
      } else {
        throw new Error(response.data?.msg || '绑定失败')
      }
    } catch (error) {
      console.error('[微信绑定] 失败', error)
      
      let errorMsg = '绑定失败'
      if (error.statusCode === 401) {
        errorMsg = '校园账号密码错误'
      } else if (error.statusCode === 404) {
        errorMsg = '校园账号不存在'
      } else if (error.data?.msg) {
        errorMsg = error.data.msg
      }

      wx.showToast({
        title: errorMsg,
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 快速体验登录
  async onGuestLogin() {
    const { formData } = this.data
    
    if (!formData.name) {
      wx.showToast({ title: '请输入姓名', icon: 'none' })
      return
    }

    const userInfo = {
      person_id: 'guest_' + Date.now(),
      person_type: 'guest',
      name: formData.name || '体验用户',
      login_id: null,
      student_id: null,
      employee_id: null,
      college_name: null,
      major_name: null,
      class_name: null,
      email: null,
      phone: null,
      wechat_bound: false,
      permissions: {
        read: ['public_data'],
        write: [],
        share: []
      }
    }

    // 保存登录信息
    wx.setStorageSync('token', 'guest_token_' + Date.now())
    wx.setStorageSync('userInfo', userInfo)
    app.globalData.userInfo = userInfo

    wx.showToast({
      title: '进入体验模式',
      icon: 'success'
    })

    setTimeout(() => {
      wx.switchTab({ url: '/pages/index/index' })
    }, 1500)
  },

  // 统一登录处理
  async onLogin() {
    const { loginType } = this.data

    if (loginType === 'wechat') {
      await this.onWechatLogin()
    } else if (loginType === 'password') {
      await this.onPasswordLogin()  
    } else if (loginType === 'guest') {
      await this.onGuestLogin()
    }
  },

  // 快速登录（测试用）
  onQuickLogin() {
    this.setData({
      loginType: 'password',
      'formData.loginId': '2025000001',
      'formData.password': 'Admin001HP1dbd10'
    })
    
    setTimeout(() => {
      this.onPasswordLogin()
    }, 300)
  },

  // 返回授权步骤
  onBackToAuth() {
    this.setData({
      wechatLoginStep: 'auth'
    })
  }
}) 