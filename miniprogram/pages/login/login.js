const app = getApp()

Page({
  data: {
    studentId: '',
    password: '',
    name: '',
    loginType: 'student', // student, admin, test
    loading: false,
    userInfo: null
  },

  onLoad() {
    // 检查是否已登录
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({ userInfo })
      this.navigateToIndex()
    }
  },

  onStudentIdInput(e) {
    this.setData({
      studentId: e.detail.value
    })
  },

  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    })
  },

  onNameInput(e) {
    this.setData({
      name: e.detail.value
    })
  },

  onLoginTypeChange(e) {
    this.setData({
      loginType: e.detail.value,
      studentId: '',
      password: '',
      name: ''
    })
  },

  async onLogin() {
    const { studentId, password, name, loginType } = this.data
    
    if (!studentId) {
      wx.showToast({
        title: '请输入学号',
        icon: 'none'
      })
      return
    }

    if (loginType === 'test' && !name) {
      wx.showToast({
        title: '请输入姓名',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    try {
      let response
      const baseUrl = app.globalData.baseUrl

      if (loginType === 'test') {
        // 测试登录
        response = await this.request(`${baseUrl}/api/v1/auth/test-login`, {
          method: 'POST',
          data: { student_id: studentId, name }
        })
      } else if (loginType === 'admin') {
        // 管理员登录 (临时使用测试接口)
        if (studentId === 'admin' && password === 'admin123') {
          response = await this.request(`${baseUrl}/api/v1/auth/test-login`, {
            method: 'POST',
            data: { student_id: 'admin', name: '系统管理员' }
          })
        } else {
          throw new Error('管理员账号密码错误')
        }
      } else {
        // 学生登录 (暂时使用测试接口)
        response = await this.request(`${baseUrl}/api/v1/auth/test-login`, {
          method: 'POST',
          data: { student_id: studentId, name: name || '学生用户' }
        })
      }

      if (response.access_token) {
        const userInfo = {
          studentId,
          name: name || (loginType === 'admin' ? '系统管理员' : '学生用户'),
          userType: loginType,
          token: response.access_token,
          isAdmin: loginType === 'admin'
        }

        // 保存用户信息
        wx.setStorageSync('userInfo', userInfo)
        wx.setStorageSync('token', response.access_token)
        
        app.globalData.userInfo = userInfo

        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })

        this.navigateToIndex()
      }
    } catch (error) {
      console.error('登录失败:', error)
      wx.showToast({
        title: '登录失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  request(url, options = {}) {
    return new Promise((resolve, reject) => {
      wx.request({
        url,
        method: options.method || 'GET',
        data: options.data,
        header: {
          'Content-Type': 'application/json',
          ...options.header
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error(res.data.detail || '请求失败'))
          }
        },
        fail: reject
      })
    })
  },

  navigateToIndex() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  onQuickLogin() {
    this.setData({
      studentId: '2024001',
      name: '张三',
      loginType: 'test'
    })
    this.onLogin()
  }
}) 