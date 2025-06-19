const app = getApp()

Page({
  data: {
    notifications: [],
    filteredNotifications: [],
    loading: true,
    searchText: '',
    currentCategory: 'all',
    categories: [
      { label: '全部', value: 'all' },
      { label: '系统通知', value: 'system' },
      { label: '课程通知', value: 'course' },
      { label: '活动通知', value: 'activity' },
      { label: '紧急通知', value: 'urgent' }
    ],
    showRefreshTip: false
  },

  onLoad() {
    console.log('[通知页面] 📢 页面加载')
    this.loadNotifications()
  },

  onShow() {
    console.log('[通知页面] 页面显示')
  },

  onPullDownRefresh() {
    console.log('[通知页面] 下拉刷新')
    this.loadNotifications()
    
    setTimeout(() => {
      wx.stopPullDownRefresh()
      this.setData({ showRefreshTip: true })
      setTimeout(() => {
        this.setData({ showRefreshTip: false })
      }, 2000)
    }, 1000)
  },

  // 加载通知数据
  loadNotifications() {
    this.setData({ loading: true })
    
    wx.request({
      url: `${app.globalData.baseURL}/api/notices`,
      method: 'GET',
      success: (response) => {
        console.log('[通知页面] 📊 通知API响应:', response)

        if (response.statusCode === 200 && response.data.code === 0) {
          const notifications = response.data.data.notices || []
          
          this.setData({
            notifications: notifications,
            loading: false
          })
          
          this.filterNotifications()
          
          console.log('[通知页面] ✅ 通知数据加载完成，共', notifications.length, '条')
        } else {
          console.error('[通知页面] ❌ 通知获取失败:', response.data)
          this.setData({
            notifications: this.getMockNotifications(),
            loading: false
          })
          
          this.filterNotifications()
          
          wx.showToast({
            title: '获取通知失败，显示示例数据',
            icon: 'none',
            duration: 2000
          })
        }
      },
      fail: (error) => {
        console.error('[通知页面] ❌ 通知请求失败:', error)
        this.setData({
          notifications: this.getMockNotifications(),
          loading: false
        })
        
        this.filterNotifications()
        
        wx.showToast({
          title: '网络异常，显示示例数据',
          icon: 'none',
          duration: 2000
        })
      }
    })
  },

  // 获取模拟通知数据
  getMockNotifications() {
    return [
      {
        id: 1,
        title: '期末考试安排通知',
        content: '本学期期末考试将于下周开始，请同学们做好考试准备...',
        department: '教务处',
        priority: 'high',
        category: 'course',
        date: '2024-06-20',
        time: '09:00'
      },
      {
        id: 2,
        title: '图书馆开放时间调整',
        content: '自下周起，图书馆开放时间将调整为8:00-22:00...',
        department: '图书馆',
        priority: 'normal',
        category: 'system',
        date: '2024-06-19',
        time: '14:30'
      },
      {
        id: 3,
        title: '校园文化节活动报名',
        content: '一年一度的校园文化节即将开始，欢迎各位同学踊跃报名参与...',
        department: '学生会',
        priority: 'normal',
        category: 'activity',
        date: '2024-06-18',
        time: '16:00'
      }
    ]
  },

  // 筛选通知
  filterNotifications() {
    let filtered = this.data.notifications

    // 按分类筛选
    if (this.data.currentCategory !== 'all') {
      filtered = filtered.filter(item => item.category === this.data.currentCategory)
    }

    // 按搜索词筛选
    if (this.data.searchText) {
      const searchText = this.data.searchText.toLowerCase()
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(searchText) ||
        item.content.toLowerCase().includes(searchText) ||
        item.department.toLowerCase().includes(searchText)
      )
    }

    this.setData({
      filteredNotifications: filtered
    })
  },

  // 分类切换
  onCategoryChange(e) {
    const category = e.currentTarget.dataset.category
    console.log('[通知页面] 🏷️ 切换分类:', category)
    
    this.setData({
      currentCategory: category
    })
    
    this.filterNotifications()
  },

  // 搜索输入
  onSearchChange(e) {
    this.setData({
      searchText: e.detail.value
    })
  },

  // 搜索提交
  onSearchSubmit(e) {
    this.setData({
      searchText: e.detail.value
    })
    this.filterNotifications()
  },

  // 查看通知详情
  viewNotification(e) {
    const notification = e.currentTarget.dataset.notification
    console.log('[通知页面] 📄 查看通知详情:', notification.title)
    
    wx.showModal({
      title: notification.title,
      content: `${notification.content}\n\n发布部门：${notification.department}\n发布时间：${notification.date} ${notification.time}`,
      showCancel: true,
      cancelText: '关闭',
      confirmText: '已读',
      confirmColor: '#0052d9',
      success: (res) => {
        if (res.confirm) {
          console.log('[通知页面] ✅ 标记为已读:', notification.title)
          // TODO: 可以在这里调用API标记为已读
        }
      }
    })
  },

  // 分享通知
  shareNotification(e) {
    const notification = e.currentTarget.dataset.notification
    console.log('[通知页面] 📤 分享通知:', notification.title)
    
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
    
    wx.showToast({
      title: '分享功能开发中',
      icon: 'none',
      duration: 1500
    })
  }
}) 