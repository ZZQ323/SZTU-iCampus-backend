const app = getApp()

Page({
  data: {
    adminInfo: {
      name: '系统管理员',
      avatar: '/assets/test/man.png'
    },
    stats: {
      user_count: 0,
      admin_count: 0,
      announcement_count: 0,
      notice_count: 0
    },
    activeTab: 'users',
    loading: false,
    users: [],
    announcements: [],
    notices: [],
    showDialog: false,
    dialogTitle: '',
    dialogContent: '',
    pendingAction: null
  },

  onLoad() {
    console.log('[管理员页面] 🔧 页面加载')
    this.checkAdminPermission()
    this.loadAdminData()
  },

  /**
   * 检查管理员权限
   */
  async checkAdminPermission() {
    try {
      const token = wx.getStorageSync('access_token')
      if (!token) {
        this.redirectToLogin()
        return
      }

      // 获取当前用户信息
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/auth/me`,
          method: 'GET',
          header: {
            'Authorization': `Bearer ${token}`
          },
          success: resolve,
          fail: reject
        })
      })

      if (response.statusCode === 200) {
        const userInfo = response.data
        if (!userInfo.is_admin) {
          wx.showModal({
            title: '权限不足',
            content: '您没有管理员权限，无法访问此页面',
            showCancel: false,
            confirmText: '返回首页',
            success: () => {
              wx.switchTab({
                url: '/pages/index/index'
              })
            }
          })
          return
        }
        
        this.setData({
          adminInfo: {
            name: userInfo.name || '管理员',
            avatar: userInfo.avatar_url || '/assets/test/man.png'
          }
        })
      } else {
        this.redirectToLogin()
      }
    } catch (error) {
      console.error('[管理员页面] 权限检查失败:', error)
      this.redirectToLogin()
    }
  },

  /**
   * 重定向到登录页面
   */
  redirectToLogin() {
    wx.showModal({
      title: '登录过期',
      content: '请重新登录',
      showCancel: false,
      confirmText: '去登录',
      success: () => {
        wx.navigateTo({
          url: '/pages/login/login'
        })
      }
    })
  },

  /**
   * 加载管理员数据
   */
  async loadAdminData() {
    this.setData({ loading: true })
    
    try {
      await Promise.all([
        this.loadStats(),
        this.loadUsers(),
        this.loadAnnouncements(),
        this.loadNotices()
      ])
    } catch (error) {
      console.error('[管理员页面] 数据加载失败:', error)
      wx.showToast({
        title: '数据加载失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  /**
   * 加载系统统计
   */
  async loadStats() {
    const token = wx.getStorageSync('access_token')
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.baseUrl}/api/admin/stats`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: resolve,
        fail: reject
      })
    })

    if (response.statusCode === 200) {
      this.setData({
        stats: response.data
      })
    }
  },

  /**
   * 加载用户列表
   */
  async loadUsers() {
    const token = wx.getStorageSync('access_token')
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.baseUrl}/api/admin/users`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: resolve,
        fail: reject
      })
    })

    if (response.statusCode === 200) {
      this.setData({
        users: response.data
      })
    }
  },

  /**
   * 加载公告列表
   */
  async loadAnnouncements() {
    const token = wx.getStorageSync('access_token')
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.baseUrl}/api/admin/announcements`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: resolve,
        fail: reject
      })
    })

    if (response.statusCode === 200) {
      this.setData({
        announcements: response.data.announcements || []
      })
    }
  },

  /**
   * 加载通知列表
   */
  async loadNotices() {
    const token = wx.getStorageSync('access_token')
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.baseUrl}/api/admin/notices`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: resolve,
        fail: reject
      })
    })

    if (response.statusCode === 200) {
      this.setData({
        notices: response.data.notices || []
      })
    }
  },

  /**
   * 选项卡切换
   */
  onTabChange(e) {
    this.setData({
      activeTab: e.detail.value
    })
  },

  /**
   * 用户点击事件
   */
  onUserClick(e) {
    const user = e.currentTarget.dataset.user
    const action = user.is_admin ? '取消管理员权限' : '设为管理员'
    
    this.setData({
      showDialog: true,
      dialogTitle: '确认操作',
      dialogContent: `确定要${action}吗？\n用户：${user.name}\n学号：${user.student_id}`,
      pendingAction: {
        type: 'toggleAdmin',
        userId: user.id,
        currentStatus: user.is_admin
      }
    })
  },

  /**
   * 删除公告
   */
  onAnnouncementDelete(e) {
    const id = e.currentTarget.dataset.id
    const announcement = this.data.announcements.find(item => item.id === id)
    
    this.setData({
      showDialog: true,
      dialogTitle: '确认删除',
      dialogContent: `确定要删除公告吗？\n标题：${announcement?.title || '未知'}`,
      pendingAction: {
        type: 'deleteAnnouncement',
        id: id
      }
    })
  },

  /**
   * 删除通知
   */
  onNoticeDelete(e) {
    const id = e.currentTarget.dataset.id
    const notice = this.data.notices.find(item => item.id === id)
    
    this.setData({
      showDialog: true,
      dialogTitle: '确认删除',
      dialogContent: `确定要删除通知吗？\n标题：${notice?.title || '未知'}`,
      pendingAction: {
        type: 'deleteNotice',
        id: id
      }
    })
  },

  /**
   * 对话框确认
   */
  async onDialogConfirm() {
    const action = this.data.pendingAction
    this.setData({ showDialog: false })

    if (!action) return

    try {
      const token = wx.getStorageSync('access_token')

      switch (action.type) {
        case 'toggleAdmin':
          await this.toggleUserAdmin(action.userId, token)
          break
        case 'deleteAnnouncement':
          await this.deleteAnnouncement(action.id, token)
          break
        case 'deleteNotice':
          await this.deleteNotice(action.id, token)
          break
      }
    } catch (error) {
      console.error('[管理员页面] 操作失败:', error)
      wx.showToast({
        title: '操作失败',
        icon: 'none'
      })
    }
  },

  /**
   * 对话框取消
   */
  onDialogCancel() {
    this.setData({
      showDialog: false,
      pendingAction: null
    })
  },

  /**
   * 切换用户管理员状态
   */
  async toggleUserAdmin(userId, token) {
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.baseUrl}/api/admin/users/${userId}/toggle-admin`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: resolve,
        fail: reject
      })
    })

    if (response.statusCode === 200) {
      wx.showToast({
        title: '操作成功',
        icon: 'success'
      })
      this.loadUsers()
      this.loadStats()
    }
  },

  /**
   * 删除公告
   */
  async deleteAnnouncement(id, token) {
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.baseUrl}/api/admin/announcements/${id}`,
        method: 'DELETE',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: resolve,
        fail: reject
      })
    })

    if (response.statusCode === 200) {
      wx.showToast({
        title: '删除成功',
        icon: 'success'
      })
      this.loadAnnouncements()
      this.loadStats()
    }
  },

  /**
   * 删除通知
   */
  async deleteNotice(id, token) {
    const response = await new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.baseUrl}/api/admin/notices/${id}`,
        method: 'DELETE',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: resolve,
        fail: reject
      })
    })

    if (response.statusCode === 200) {
      wx.showToast({
        title: '删除成功',
        icon: 'success'
      })
      this.loadNotices()
      this.loadStats()
    }
  },

  /**
   * 刷新数据
   */
  refreshData() {
    wx.showLoading({
      title: '刷新中...'
    })
    
    this.loadAdminData().then(() => {
      wx.hideLoading()
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    })
  },

  /**
   * 打开设置
   */
  openSettings() {
    wx.showModal({
      title: '系统设置',
      content: '设置功能正在开发中...',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  /**
   * 返回首页
   */
  goHome() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.refreshData()
    wx.stopPullDownRefresh()
  },

  onShow() {
    console.log('[管理员页面] 👀 页面显示')
  },

  onHide() {
    console.log('[管理员页面] 页面隐藏')
  }
}) 