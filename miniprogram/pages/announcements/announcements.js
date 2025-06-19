const app = getApp()

// Page(options) options 是一个对象，属性会被直接挂到页面实例上

Page({
  data: {
    announcements: [],
    filteredAnnouncements: [],
    searchText: '',
    currentCategory: 'all',
    categories: [
      { label: '全部', value: 'all' },
      { label: '教务', value: 'academic' },
      { label: '学工', value: 'student' },
      { label: '后勤', value: 'logistics' },
      { label: '重要', value: 'important' }
    ],
    loading: false,
    showRefreshTip: false
  },
  onLoad() {
    // 参数 query 携带通过 ? 拼接的 URL 查询参数
    // 第一次加载执行一次
    this.fetchAnnouncements()
  },

  onShow() {
    // 页面显示时刷新数据
    // 页面每次可见时调用。常用来刷新 UI、重连 WebSocket 等
    if (this.data.announcements.length === 0) {
      this.fetchAnnouncements()
    }
  },

  async fetchAnnouncements() {
    this.setData({ loading: true })

    try {
      // 模拟获取数据
      const mockData = this.generateMockAnnouncements()
      
      this.setData({
        announcements: mockData,
        filteredAnnouncements: mockData
      })
      
      this.filterAnnouncements()
    } catch (error) {
      console.error('获取公告失败:', error)
      wx.showToast({
        title: '获取公告失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 生成模拟数据
  generateMockAnnouncements() {
    return [
      {
        id: 1,
        title: '关于2024年春季学期期末考试安排的通知',
        content: '根据学校教学计划安排，现将2024年春季学期期末考试相关事宜通知如下：考试时间为6月10日-6月20日，请各位同学提前做好复习准备...',
        department: '教务处',
        category: 'academic',
        priority: 'high',
        date: '2024-05-20',
        time: '14:30',
        isRead: false
      },
      {
        id: 2,
        title: '深圳技术大学第十届科技文化节活动通知',
        content: '为丰富校园文化生活，激发学生创新创业热情，学校将于5月25日-6月5日举办第十届科技文化节...',
        department: '学工部',
        category: 'student',
        priority: 'normal',
        date: '2024-05-18',
        time: '10:15',
        isRead: true
      },
      {
        id: 3,
        title: '图书馆系统维护通知',
        content: '因系统升级需要，图书馆将于5月22日18:00-23:00进行系统维护，期间无法正常使用借阅服务...',
        department: '图书馆',
        category: 'logistics',
        priority: 'normal',
        date: '2024-05-17',
        time: '16:45',
        isRead: false
      },
      {
        id: 4,
        title: '关于调整校园网络服务的重要通知',
        content: '为提升校园网络服务质量，网络中心将对校园网进行重要升级改造，具体安排如下...',
        department: '网络中心',
        category: 'important',
        priority: 'high',
        date: '2024-05-16',
        time: '09:20',
        isRead: true
      },
      {
        id: 5,
        title: '夏季用电安全提醒',
        content: '随着夏季来临，用电量增加，为确保校园用电安全，请各位师生注意以下事项...',
        department: '后勤处',
        category: 'logistics',
        priority: 'normal',
        date: '2024-05-15',
        time: '11:30',
        isRead: false
      }
    ]
  },

  // 搜索功能
  onSearchChange(e) {
    this.setData({
      searchText: e.detail.value
    })
    this.filterAnnouncements()
  },

  onSearchSubmit(e) {
    this.setData({
      searchText: e.detail.value
    })
    this.filterAnnouncements()
  },

  // 分类切换
  onCategoryChange(e) {
    const category = e.currentTarget.dataset.category
    this.setData({
      currentCategory: category
    })
    this.filterAnnouncements()
  },

  // 过滤公告
  filterAnnouncements() {
    const { announcements, searchText, currentCategory } = this.data
    
    let filtered = announcements

    // 按分类过滤
    if (currentCategory !== 'all') {
      if (currentCategory === 'important') {
        filtered = filtered.filter(item => item.priority === 'high')
      } else {
        filtered = filtered.filter(item => item.category === currentCategory)
      }
    }

    // 按搜索关键词过滤
    if (searchText.trim()) {
      const keyword = searchText.trim().toLowerCase()
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(keyword) ||
        item.content.toLowerCase().includes(keyword) ||
        item.department.toLowerCase().includes(keyword)
      )
    }

    this.setData({
      filteredAnnouncements: filtered
    })
  },

  // 查看公告详情
  viewAnnouncement(e) {
    const announcement = e.currentTarget.dataset.announcement
    
    // 标记为已读
    const updatedAnnouncements = this.data.announcements.map(item => {
      if (item.id === announcement.id) {
        return { ...item, isRead: true }
      }
      return item
    })
    
    this.setData({
      announcements: updatedAnnouncements
    })
    this.filterAnnouncements()

    // 跳转到详情页
    app.globalData.currentAnnouncement = announcement
    wx.navigateTo({
      url: '/pages/announcement-detail/announcement-detail'
    })
  },

  // 分享公告
  shareAnnouncement(e) {
    const announcement = e.currentTarget.dataset.announcement
    
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })

    wx.showToast({
      title: '分享功能已开启',
      icon: 'success'
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.setData({ showRefreshTip: true })
    
    this.fetchAnnouncements().then(() => {
      wx.stopPullDownRefresh()
      this.setData({ showRefreshTip: false })
      
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    })
  },

  onBack() {
    // delta 表示返回几层，1 = 上一页。
    wx.navigateBack({
      delta: 1
    });
  }
}); 