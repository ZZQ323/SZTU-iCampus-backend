const app = getApp()
const API = require('../../utils/api.js')

Page({
  data: {
    // 用户状态
    userInfo: null,
    isLoggedIn: false,
    
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
    this.checkLoginStatus()
  },

  onShow() {
    this.checkLoginStatus()
  },

  /**
   * 检查登录状态和管理员权限
   */
  checkLoginStatus() {
    const userInfo = wx.getStorageSync('userInfo')
    
    if (!userInfo) {
      this.showLoginPrompt()
      return
    }

    this.setData({
      isLoggedIn: true,
      userInfo: userInfo
    })

    // 验证管理员权限
    this.checkAdminPermission()
  },

  /**
   * 显示登录提示
   */
  showLoginPrompt() {
    wx.showModal({
      title: '需要登录',
      content: '管理页面需要登录后才能访问，请先登录',
      showCancel: true,
      cancelText: '返回首页',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: '/pages/login/login'
          })
        } else {
          wx.switchTab({
            url: '/pages/index/index'
          })
        }
      }
    })
  },

  // 检查管理员权限
  checkAdminPermission() {
    const userInfo = this.data.userInfo
    
    // 定义可以访问管理页面的用户类型
    const adminTypes = ['admin', 'dean', 'department_head', 'major_director', 'counselor', 'class_advisor', 'librarian']
    const isAdmin = adminTypes.includes(userInfo.person_type);
    
    if (!isAdmin) {
      wx.showModal({
        title: '权限不足',
        content: `您的身份是"${this.getPersonTypeName(userInfo.person_type)}"，没有管理员权限，无法访问此页面。`,
        showCancel: true,
        cancelText: '返回首页',
        confirmText: '确定',
        success: (res) => {
          if (res.cancel) {
            wx.switchTab({
              url: '/pages/index/index'
            });
          } else {
            wx.navigateBack();
          }
        }
      });
      return false;
    }
    
    // 设置管理员信息
    this.setData({
      adminInfo: {
        name: userInfo.name || '管理员',
        avatar: userInfo.avatar || '',
        type: userInfo.person_type,
        typeName: this.getPersonTypeName(userInfo.person_type),
        college: userInfo.college_name,
        department: userInfo.department_name
      }
    });

    // 初始化数据
    this.initializeData();
    this.fetchData();
    
    return true;
  },

  /**
   * 获取人员类型中文名称
   */
  getPersonTypeName(personType) {
    const typeNames = {
      'admin': '系统管理员',
      'department_head': '部门主管',
      'dean': '院长',
      'major_director': '专业主任',
      'student': '学生',
      'teacher': '教师',
      'assistant_teacher': '助教',
      'counselor': '辅导员',
      'class_advisor': '班主任',
      'librarian': '图书管理员'
    };
    return typeNames[personType] || '未知身份';
  },

  // 初始化数据
  initializeData() {
    const userType = this.data.userInfo.person_type;
    
    // 根据管理员类型生成不同的操作记录
    let recentActions = [];
    
    if (userType === 'admin') {
      recentActions = [
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
      ];
    } else if (userType === 'dean') {
      recentActions = [
        {
          id: 1,
          icon: '📋',
          action: '审批了教师申请',
          time: '5分钟前',
          status: 'success',
          statusText: '已批准'
        },
        {
          id: 2,
          icon: '📊',
          action: '查看了学院统计数据',
          time: '20分钟前',
          status: 'info',
          statusText: '已查看'
        },
        {
          id: 3,
          icon: '📝',
          action: '发布了学院通知',
          time: '1小时前',
          status: 'success',
          statusText: '已发布'
        }
      ];
    } else if (userType === 'department_head') {
      recentActions = [
        {
          id: 1,
          icon: '👥',
          action: '处理了部门事务',
          time: '10分钟前',
          status: 'success',
          statusText: '已处理'
        },
        {
          id: 2,
          icon: '📄',
          action: '审核了部门报告',
          time: '30分钟前',
          status: 'success',
          statusText: '已审核'
        }
      ];
    } else {
      recentActions = [
        {
          id: 1,
          icon: '📋',
          action: '查看了管理数据',
          time: '15分钟前',
          status: 'info',
          statusText: '已查看'
        }
      ];
    }
    
    this.setData({ recentActions });
  },

  // 获取统计数据
  async fetchData() {
    this.setData({ loading: true })
    
    try {
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
    try {
      const response = await API.getAdminStats()
      
      if (response.code === 0) {
        const data = response.data || {}
        const userType = this.data.userInfo.person_type;
        
        // 根据管理员类型返回相应的统计数据
        let stats = {};
        
        if (userType === 'admin') {
          // 系统管理员可以看到全局数据
          stats = {
            userCount: data.total_users || 0,
            adminCount: data.admin_count || 0,
            announcementCount: data.total_announcements || 0,
            noticeCount: data.total_notices || 0,
            activeUsers: data.active_users || 0,
            systemLoad: data.system_load || '0%'
          };
        } else if (userType === 'dean') {
          // 院长看到学院数据
          stats = {
            userCount: data.college_users || 0,
            adminCount: data.college_admins || 0,
            announcementCount: data.college_announcements || 0,
            noticeCount: data.college_notices || 0,
            facultyCount: data.faculty_count || 0,
            studentCount: data.student_count || 0
          };
        } else if (userType === 'department_head') {
          // 部门主管看到部门数据
          stats = {
            userCount: data.department_users || 0,
            adminCount: data.department_admins || 0,
            announcementCount: data.department_announcements || 0,
            noticeCount: data.department_notices || 0,
            staffCount: data.staff_count || 0,
            activeProjects: data.active_projects || 0
          };
        } else {
          // 其他类型的管理员
          stats = {
            userCount: data.managed_users || 0,
            adminCount: 1,
            announcementCount: data.managed_announcements || 0,
            noticeCount: data.managed_notices || 0
          };
        }
        
        return stats;
      } else {
        throw new Error(response.message || '获取统计数据失败')
      }
    } catch (error) {
      console.error('[管理员页面] ❌ 获取统计数据失败:', error)
      
      // 返回默认数据
      const userType = this.data.userInfo.person_type;
      
      if (userType === 'admin') {
        return {
          userCount: 0,
          adminCount: 0,
          announcementCount: 0,
          noticeCount: 0,
          activeUsers: 0,
          systemLoad: '0%'
        };
      } else if (userType === 'dean') {
        return {
          userCount: 0,
          adminCount: 0,
          announcementCount: 0,
          noticeCount: 0,
          facultyCount: 0,
          studentCount: 0
        };
      } else if (userType === 'department_head') {
        return {
          userCount: 0,
          adminCount: 0,
          announcementCount: 0,
          noticeCount: 0,
          staffCount: 0,
          activeProjects: 0
        };
      } else {
        return {
          userCount: 0,
          adminCount: 1,
          announcementCount: 0,
          noticeCount: 0
        };
      }
    }
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
    const userType = this.data.userInfo.person_type;
    
    if (userType !== 'admin') {
      wx.showToast({
        title: '只有系统管理员可以添加管理员',
        icon: 'none'
      });
      return;
    }
    
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
    const userType = this.data.userInfo.person_type;
    
    if (userType !== 'admin') {
      wx.showToast({
        title: '只有系统管理员可以查看系统日志',
        icon: 'none'
      });
      return;
    }

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
    const userType = this.data.userInfo.person_type;
    
    if (userType !== 'admin') {
      wx.showToast({
        title: '只有系统管理员可以修改系统设置',
        icon: 'none'
      });
      return;
    }

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
    const userType = this.data.userInfo.person_type;
    
    if (userType !== 'admin') {
      wx.showToast({
        title: '只有系统管理员可以执行数据备份',
        icon: 'none'
      });
      return;
    }

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
  async startBackup() {
    try {
      wx.showLoading({
        title: '备份中...'
      })
      
      const response = await API.createSystemBackup()
      
      if (response.code === 0) {
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
      } else {
        throw new Error(response.message || '备份失败')
      }
    } catch (error) {
      console.error('[管理员页面] ❌ 备份失败:', error)
      wx.hideLoading()
      wx.showToast({
        title: '备份失败，请重试',
        icon: 'none'
      })
    }
  },

  // 刷新数据
  onPullDownRefresh() {
    this.checkLoginStatus();
    this.fetchData().then(() => {
      wx.stopPullDownRefresh()
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    })
  }
}) 