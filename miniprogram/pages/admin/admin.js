const app = getApp()

Page({
  data: {
    adminInfo: {
      name: '系统管理员',
      avatar: ''
    },
    stats: {
      userCount: 0,
      adminCount: 0,
      announcementCount: 0,
      noticeCount: 0
    },
    recentActions: [],
    loading: false,
    
    // 弹窗控制
    showUserActions: false,
    showAdminDialog: false,
    
    // 用户操作选项
    userActionItems: [
      { label: '查看用户列表', value: 'list' },
      { label: '添加新用户', value: 'add' },
      { label: '批量导入用户', value: 'import' },
      { label: '用户数据导出', value: 'export' }
    ],
    
    // 管理员对话框
    adminDialogContent: '请选择要执行的管理员操作',
    adminDialogActions: [
      { label: '取消', value: 'cancel' },
      { label: '查看管理员列表', value: 'list' },
      { label: '添加管理员', value: 'add' }
    ]
  },

  onLoad() {
    this.checkAdminPermission()
    this.initializeData()
  },

  onShow() {
    this.fetchData()
  },

  // 检查管理员权限
  checkAdminPermission() {
    const userInfo = wx.getStorageSync('userInfo')
    
    if (!userInfo || !userInfo.is_admin) {
      wx.showModal({
        title: '权限不足',
        content: '您没有管理员权限，无法访问此页面',
        showCancel: false,
        success: () => {
          wx.navigateBack()
        }
      })
      return false
    }
    
    this.setData({
      adminInfo: {
        name: userInfo.name || '管理员',
        avatar: userInfo.avatar || ''
      }
    })
    
    return true
  },

  // 初始化数据
  initializeData() {
    // 生成最近操作记录
    const recentActions = [
      {
        id: 1,
        icon: '👤',
        action: '添加了新用户 张三',
        time: '2分钟前',
        status: 'success',
        statusText: '成功'
      },
      {
        id: 2,
        icon: '📢',
        action: '发布了新公告"期末考试安排"',
        time: '10分钟前',
        status: 'success',
        statusText: '成功'
      },
      {
        id: 3,
        icon: '⚙️',
        action: '修改了系统设置',
        time: '30分钟前',
        status: 'success',
        statusText: '成功'
      },
      {
        id: 4,
        icon: '🗑️',
        action: '删除了过期通知',
        time: '1小时前',
        status: 'warning',
        statusText: '已处理'
      }
    ]
    
    this.setData({ recentActions })
  },

  // 获取统计数据
  async fetchData() {
    this.setData({ loading: true })
    
    try {
      // 模拟获取统计数据
      const stats = await this.fetchStats()
      this.setData({ stats })
    } catch (error) {
      console.error('获取管理员数据失败:', error)
      wx.showToast({
        title: '获取数据失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 获取统计数据
  async fetchStats() {
    // 模拟API调用
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          userCount: 156,
          adminCount: 5,
          announcementCount: 23,
          noticeCount: 45
        })
      }, 1000)
    })
  },

  // 用户管理
  navigateToUserList() {
    wx.showToast({
      title: '用户列表功能开发中',
      icon: 'none'
    })
  },

  showUserActions() {
    this.setData({ showUserActions: true })
  },

  hideUserActions() {
    this.setData({ showUserActions: false })
  },

  onUserActionClick(e) {
    const action = e.detail.value
    this.setData({ showUserActions: false })
    
    switch (action) {
      case 'list':
        this.navigateToUserList()
        break
      case 'add':
        this.addNewUser()
        break
      case 'import':
        this.importUsers()
        break
      case 'export':
        this.exportUsers()
        break
    }
  },

  addNewUser() {
    wx.showToast({
      title: '添加用户功能开发中',
      icon: 'none'
    })
  },

  importUsers() {
    wx.showToast({
      title: '批量导入功能开发中',
      icon: 'none'
    })
  },

  exportUsers() {
    wx.showToast({
      title: '数据导出功能开发中',
      icon: 'none'
    })
  },

  // 管理员设置
  showAdminManagement() {
    this.setData({ showAdminDialog: true })
  },

  onAdminDialogAction(e) {
    const action = e.detail.value
    this.setData({ showAdminDialog: false })
    
    switch (action) {
      case 'list':
        this.viewAdminList()
        break
      case 'add':
        this.addNewAdmin()
        break
    }
  },

  viewAdminList() {
    wx.showToast({
      title: '管理员列表功能开发中',
      icon: 'none'
    })
  },

  addNewAdmin() {
    wx.showToast({
      title: '添加管理员功能开发中',
      icon: 'none'
    })
  },

  // 内容管理
  manageAnnouncements() {
    wx.showModal({
      title: '公告管理',
      content: '是否跳转到公告管理页面？',
      success: (res) => {
        if (res.confirm) {
          wx.switchTab({
            url: '/pages/announcements/announcements'
          })
        }
      }
    })
  },

  manageNotices() {
    wx.showModal({
      title: '通知管理',
      content: '是否跳转到通知管理页面？',
      success: (res) => {
        if (res.confirm) {
          wx.switchTab({
            url: '/pages/notices/notices'
          })
        }
      }
    })
  },

  manageEvents() {
    wx.showModal({
      title: '活动管理',
      content: '是否跳转到活动管理页面？',
      success: (res) => {
        if (res.confirm) {
          wx.switchTab({
            url: '/pages/events/events'
          })
        }
      }
    })
  },

  // 系统管理
  viewSystemLogs() {
    wx.showActionSheet({
      itemList: ['查看登录日志', '查看操作日志', '查看错误日志', '清理日志'],
      success: (res) => {
        const actions = ['login', 'operation', 'error', 'clean']
        const action = actions[res.tapIndex]
        
        wx.showToast({
          title: `${['登录日志', '操作日志', '错误日志', '清理日志'][res.tapIndex]}功能开发中`,
          icon: 'none'
        })
      }
    })
  },

  showSystemSettings() {
    wx.showActionSheet({
      itemList: ['系统配置', '安全设置', '备份设置', '邮件设置'],
      success: (res) => {
        wx.showToast({
          title: `${['系统配置', '安全设置', '备份设置', '邮件设置'][res.tapIndex]}功能开发中`,
          icon: 'none'
        })
      }
    })
  },

  showDataBackup() {
    wx.showActionSheet({
      itemList: ['立即备份', '恢复数据', '备份历史', '自动备份设置'],
      success: (res) => {
        const actions = ['backup', 'restore', 'history', 'auto']
        const action = actions[res.tapIndex]
        
        switch (action) {
          case 'backup':
            this.startBackup()
            break
          default:
            wx.showToast({
              title: `${['立即备份', '恢复数据', '备份历史', '自动备份设置'][res.tapIndex]}功能开发中`,
              icon: 'none'
            })
        }
      }
    })
  },

  // 数据备份
  startBackup() {
    wx.showLoading({
      title: '备份中...'
    })
    
    // 模拟备份过程
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({
        title: '备份完成',
        icon: 'success'
      })
      
      // 添加到最近操作
      const newAction = {
        id: Date.now(),
        icon: '💾',
        action: '执行了数据备份',
        time: '刚刚',
        status: 'success',
        statusText: '成功'
      }
      
      const recentActions = [newAction, ...this.data.recentActions.slice(0, 3)]
      this.setData({ recentActions })
    }, 2000)
  },

  // 刷新数据
  onPullDownRefresh() {
    this.fetchData().then(() => {
      wx.stopPullDownRefresh()
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    })
  }
}) 