const app = getApp()

Page({
  data: {
    loginType: 'student', // student, admin, guest
    formData: {
      studentId: '',
      password: '',
      name: ''
    },
    loading: false
  },

  onLoad() {
    console.log('[登录] 页面加载')
    this.checkExistingLogin()
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

  // 切换登录类型
  onLoginTypeChange(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      loginType: type,
      formData: {
        studentId: '',
        password: '',
        name: ''
      }
    })
  },

  // 输入处理
  onStudentIdInput(e) {
    this.setData({
      'formData.studentId': e.detail.value
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

  // 登录处理
  async onLogin() {
    const { loginType, formData } = this.data

    // 表单验证
    if (!this.validateForm()) {
      return
    }

    this.setData({ loading: true })

    try {
      let result
      
      if (loginType === 'student') {
        result = await this.studentLogin()
      } else if (loginType === 'admin') {
        result = await this.adminLogin()
      } else if (loginType === 'guest') {
        result = await this.guestLogin()
      }

      if (result.success) {
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    } catch (error) {
      wx.showToast({
        title: error.message || '登录失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 表单验证
  validateForm() {
    const { loginType, formData } = this.data

    if (loginType === 'student') {
      if (!formData.studentId) {
        wx.showToast({ title: '请输入学号', icon: 'none' })
        return false
      }
      if (!formData.password) {
        wx.showToast({ title: '请输入密码', icon: 'none' })
        return false
      }
    } else if (loginType === 'admin') {
      if (!formData.studentId) {
        wx.showToast({ title: '请输入管理员账号', icon: 'none' })
        return false
      }
      if (!formData.password) {
        wx.showToast({ title: '请输入密码', icon: 'none' })
        return false
      }
    } else if (loginType === 'guest') {
      if (!formData.name) {
        wx.showToast({ title: '请输入姓名', icon: 'none' })
        return false
      }
    }

    return true
  },

  // 学生登录
  async studentLogin() {
    const { formData } = this.data
    
    try {
      const response = await wx.request({
        url: `${app.globalData.baseURL}/api/v1/auth/login`,
        method: 'POST',
        data: {
          student_id: formData.studentId,
          password: formData.password
        }
      })

      if (response.data && response.data.access_token) {
        const userInfo = {
          name: formData.studentId,
          studentId: formData.studentId,
          is_admin: false
        }

        // 保存登录信息
        wx.setStorageSync('token', response.data.access_token)
        wx.setStorageSync('userInfo', userInfo)

        return { success: true }
      } else {
        throw new Error('登录失败')
      }
    } catch (error) {
      console.error('学生登录失败:', error)
      throw new Error('账号或密码错误')
    }
  },

  // 管理员登录
  async adminLogin() {
    const { formData } = this.data
    
    // 简单的管理员验证
    if (formData.studentId === 'admin' && formData.password === 'admin123') {
      const userInfo = {
        name: '管理员',
        studentId: 'admin',
        is_admin: true
      }

      // 保存登录信息
      wx.setStorageSync('token', 'admin_token_' + Date.now())
      wx.setStorageSync('userInfo', userInfo)

      return { success: true }
    } else {
      throw new Error('管理员账号或密码错误')
    }
  },

  // 快速体验登录
  async guestLogin() {
    const { formData } = this.data
    
    const userInfo = {
      name: formData.name || '体验用户',
      studentId: 'guest_' + Date.now(),
      is_admin: false
    }

    // 保存登录信息
    wx.setStorageSync('token', 'guest_token_' + Date.now())
    wx.setStorageSync('userInfo', userInfo)

    return { success: true }
  },

  // 快速登录（张三）
  onQuickLogin() {
    this.setData({
      loginType: 'guest',
      'formData.name': '张三'
    })
    
    setTimeout(() => {
      this.onLogin()
    }, 300)
  }
}) 