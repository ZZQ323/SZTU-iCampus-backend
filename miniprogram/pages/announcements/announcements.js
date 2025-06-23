const app = getApp()
const API = require('../../utils/api')

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
      // 调用真实API获取公告数据
      const announcementsData = await API.getAnnouncements({
        page: 1,
        size: 50,
        sort: 'publish_time',
        order: 'desc'
      })
      
      // 转换数据格式
      const announcements = (announcementsData.announcements || []).map(item => ({
        id: item.announcement_id,
        title: item.title,
        content: item.content || item.summary || '',
        department: item.department,
        category: this.mapCategoryFromApi(item.category),
        priority: item.priority === 'high' ? 'high' : 'normal',
        date: item.publish_time ? item.publish_time.split('T')[0] : '',
        time: item.publish_time ? item.publish_time.split('T')[1].substring(0, 5) : '',
        isRead: false, // 后续可以通过阅读记录API获取
        isUrgent: item.is_urgent,
        isPinned: item.is_pinned,
        viewCount: item.view_count || 0
      }))
      
      this.setData({
        announcements: announcements,
        filteredAnnouncements: announcements
      })
      
      this.filterAnnouncements()
    } catch (error) {
      console.error('获取公告失败:', error)
      wx.showToast({
        title: '获取公告失败',
        icon: 'none'
      })
      
      // 失败时使用备用数据
      this.setData({
        announcements: [],
        filteredAnnouncements: []
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  /**
   * 将API返回的分类映射到前端分类
   */
  mapCategoryFromApi(apiCategory) {
    const categoryMap = {
      'education': 'academic',
      'academic': 'academic',
      'student_affairs': 'student',
      'logistics': 'logistics',
      'system': 'logistics',
      'sports': 'student',
      'general': 'academic'
    }
    return categoryMap[apiCategory] || 'academic'
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
  async viewAnnouncement(e) {
    const announcement = e.currentTarget.dataset.announcement
    
    try {
      // 调用API标记为已读
      await API.markAnnouncementRead(announcement.id)
      
      // 记录阅读行为
      await API.recordReading('announcement', announcement.id, 0)
      
      // 本地标记为已读
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
    } catch (error) {
      console.error('标记已读失败:', error)
      // 即使标记失败也继续跳转
    }

    // 跳转到详情页
    app.globalData.currentAnnouncement = announcement
    wx.navigateTo({
      url: `/pages/announcement-detail/announcement-detail?id=${announcement.id}`
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