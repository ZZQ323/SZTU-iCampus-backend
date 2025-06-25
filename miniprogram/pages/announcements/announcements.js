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
      { label: '重要', value: 'important' },
      { label: '收藏', value: 'collected' }
    ],
    currentSort: 'time_desc',
    currentSortLabel: '最新发布',
    showSortMenu: false,
    sortOptions: [
      { label: '最新发布', value: 'time_desc', icon: '⏰' },
      { label: '最早发布', value: 'time_asc', icon: '📅' },
      { label: '重要在前', value: 'priority_desc', icon: '⚠️' },
      { label: '置顶在前', value: 'pinned_desc', icon: '📌' },
      { label: '浏览量高', value: 'views_desc', icon: '👁️' },
      { label: '标题排序', value: 'title_asc', icon: '🔤' }
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
    } else {
      // 如果公告数据已存在，更新收藏状态并重新过滤
      this.updateCollectionStatus()
      this.filterAnnouncements()
    }
    
    // 注册实时更新事件监听
    this.setupRealtimeUpdates()
  },

  onHide() {
    // 页面隐藏时移除事件监听
    this.removeRealtimeListeners()
  },

  onUnload() {
    // 页面卸载时移除事件监听
    this.removeRealtimeListeners()
  },

  // 设置实时更新监听
  setupRealtimeUpdates() {
    console.log('🎧 公告页面：开始设置实时更新监听...');
    
    const streamManager = getApp().globalData.streamManager
    if (!streamManager) {
      console.error('❌ StreamManager 未找到！');
      return;
    }
    
    console.log('✅ StreamManager 已找到，设置监听器...');
    
    // 监听实时更新事件
    streamManager.addEventListener('realtime_update', this.handleRealtimeUpdate.bind(this))
    
    // 监听增量同步事件
    streamManager.addEventListener('incremental_sync', this.handleIncrementalSync.bind(this))
    
    // 监听公告更新事件（重要：直接监听缓存更新）
    streamManager.addEventListener('announcements_updated', this.handleAnnouncementsUpdated.bind(this))
    
    console.log('📡 公告页面已注册实时更新监听');
    
    // 添加调试：检查轮询状态
    if (streamManager.pollingTimer) {
      console.log('✅ 事件轮询已启动');
    } else {
      console.warn('⚠️ 事件轮询未启动，手动启动...');
      streamManager.startPollingForEvents();
    }
  },

  // 移除实时更新监听
  removeRealtimeListeners() {
    const streamManager = getApp().globalData.streamManager
    if (streamManager) {
      streamManager.removeEventListener('realtime_update', this.handleRealtimeUpdate.bind(this))
      streamManager.removeEventListener('incremental_sync', this.handleIncrementalSync.bind(this))
      streamManager.removeEventListener('announcements_updated', this.handleAnnouncementsUpdated.bind(this))
    }
  },

  // 处理实时更新
  handleRealtimeUpdate(data) {
    if (data.events && data.events.length > 0) {
      // 检查是否有新公告
      const newAnnouncements = data.events.filter(event => 
        event.event_type === 'announcement' || 
        event.event_type === 'notice' || 
        event.event_type === 'system_message'
      )
      
      if (newAnnouncements.length > 0) {
        console.log(`📢 收到 ${newAnnouncements.length} 个新公告，刷新列表`)
        
        // 显示新公告提示
        wx.showToast({
          title: `收到${newAnnouncements.length}条新公告`,
          icon: 'success',
          duration: 2000
        })
        
        // 刷新公告列表
        this.fetchAnnouncements()
      }
    }
  },

  // 处理增量同步
  handleIncrementalSync(data) {
    if (data.eventsByType && data.eventsByType.announcement) {
      console.log('📋 检测到公告增量同步，刷新数据')
      this.fetchAnnouncements()
    }
  },

  // 处理公告缓存更新事件（重要：直接更新UI）
  handleAnnouncementsUpdated(data) {
    console.log('🔥🔥🔥 公告页面收到缓存更新事件:', data)
    
    if (data.announcements) {
      // 直接使用缓存的公告数据，转换为页面需要的格式
      const announcements = data.announcements.map(item => ({
        id: item.announcement_id || item.id,
        announcement_id: item.announcement_id || item.id,
        title: item.title,
        content: item.content || '',
        department: item.department || '系统',
        category: this.mapCategoryFromCache(item.category),
        priority: item.priority || 'normal',
        publishTime: item.publish_time || item.publishTime || item.timestamp,
        date: item.publish_time ? item.publish_time.split('T')[0] : 
              item.publishTime ? item.publishTime.split('T')[0] : 
              new Date().toISOString().split('T')[0],
        time: item.publish_time && item.publish_time.includes('T') 
          ? item.publish_time.split('T')[1].substring(0, 5) 
          : item.publishTime && item.publishTime.includes('T')
          ? item.publishTime.split('T')[1].substring(0, 5)
          : '00:00',
        isRead: item.isRead || false,
        isUrgent: item.is_urgent || item.isUrgent || false,
        isPinned: item.is_pinned || item.isPinned || false,
        viewCount: item.viewCount || 0
      }))
      
      console.log(`📋📋📋 实时更新公告列表，共 ${announcements.length} 条`)
      
      // 🔥 关键修复：同时更新两个数据源，确保页面立即更新
      this.setData({
        announcements: announcements,
        filteredAnnouncements: announcements  // 强制同时更新显示数据
      })
      
      // 立即重新应用过滤和排序
      this.filterAnnouncements()
      
      // 显示更新提示
      const changeCount = data.changeEvents ? data.changeEvents.length : 0
      if (changeCount > 0) {
        console.log(`🎉 强制页面更新完成: ${changeCount} 个变更`);
        
        wx.showToast({
          title: `公告实时更新`,
          icon: 'success',
          duration: 1500
        })
      }
      
      console.log(`🎉🎉🎉 页面数据已强制更新！announcements: ${this.data.announcements.length}, filtered: ${this.data.filteredAnnouncements.length}`)
    } else {
      console.warn('⚠️ 公告更新事件中没有announcements数据');
    }
  },

  /**
   * 映射缓存分类到前端分类
   */
  mapCategoryFromCache(cacheCategory) {
    const categoryMap = {
      'education': 'academic',
      'academic': 'academic',
      'student_affairs': 'student',
      'logistics': 'logistics',
      'system': 'logistics',
      'sports': 'student',
      'general': 'academic'
    }
    return categoryMap[cacheCategory] || 'academic'
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
      
      // 转换数据格式 - 🔧 修复数据访问路径
      const announcements = (announcementsData.data?.announcements || []).map(item => ({
        id: item.announcement_id,
        title: item.title,
        content: item.content || item.summary || '',
        department: item.department,
        category: this.mapCategoryFromApi(item.category),
        priority: item.priority === 'high' ? 'high' : 'normal',
        publishTime: item.publish_time || new Date().toISOString(), // 保存完整时间用于排序
        date: item.publish_time ? item.publish_time.split('T')[0] : new Date().toISOString().split('T')[0],
        time: item.publish_time && item.publish_time.includes('T') 
          ? item.publish_time.split('T')[1].substring(0, 5) 
          : '00:00',
        isRead: false, // 后续可以通过阅读记录API获取
        isUrgent: item.is_urgent || false,
        isPinned: item.is_pinned || false,
        viewCount: item.view_count || 0
      }))
      
      this.setData({
        announcements: announcements,
        filteredAnnouncements: announcements
      })
      
      // 更新收藏状态
      this.updateCollectionStatus()
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
    const { announcements, searchText, currentCategory, currentSort } = this.data
    
    let filtered = announcements

    // 按分类过滤
    if (currentCategory !== 'all') {
      if (currentCategory === 'important') {
        filtered = filtered.filter(item => item.priority === 'high')
      } else if (currentCategory === 'collected') {
        // 收藏分类：从本地存储获取已收藏的公告
        const collectedAnnouncements = wx.getStorageSync('collectedAnnouncements') || []
        const collectedIds = new Set(collectedAnnouncements.map(item => item.id))
        filtered = filtered.filter(item => collectedIds.has(item.id))
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

    // 应用排序
    filtered = this.sortAnnouncements(filtered, currentSort)

    this.setData({
      filteredAnnouncements: filtered
    })
  },

  // 排序功能 - 修复版本
  sortAnnouncements(announcements, sortType) {
    if (!announcements || announcements.length === 0) {
      return []
    }
    
    const sorted = [...announcements]
    
    // 安全的时间解析函数
    const parseTime = (item) => {
      try {
        // 优先使用publishTime，如果没有则构造
        if (item.publishTime) {
          return new Date(item.publishTime).getTime()
        }
        
        // 从date和time构造时间
        if (item.date && item.time) {
          const dateStr = `${item.date}T${item.time}:00`
          return new Date(dateStr).getTime()
        }
        
        // 只有date
        if (item.date) {
          return new Date(item.date).getTime()
        }
        
        // 都没有，返回当前时间
        return new Date().getTime()
      } catch (e) {
        console.warn('时间解析失败:', item, e)
        return new Date().getTime()
      }
    }
    
    switch (sortType) {
      case 'time_desc':
        return sorted.sort((a, b) => {
          const timeA = parseTime(a)
          const timeB = parseTime(b)
          return timeB - timeA
        })
      
      case 'time_asc':
        return sorted.sort((a, b) => {
          const timeA = parseTime(a)
          const timeB = parseTime(b)
          return timeA - timeB
        })
      
      case 'priority_desc':
        return sorted.sort((a, b) => {
          // 置顶 > 紧急 > 高优先级 > 普通
          const pinnedA = a.isPinned || false
          const pinnedB = b.isPinned || false
          const urgentA = a.isUrgent || false
          const urgentB = b.isUrgent || false
          const priorityA = a.priority || 'normal'
          const priorityB = b.priority || 'normal'
          
          if (pinnedA !== pinnedB) return pinnedB - pinnedA
          if (urgentA !== urgentB) return urgentB - urgentA
          if (priorityA !== priorityB) {
            return priorityA === 'high' ? -1 : priorityB === 'high' ? 1 : 0
          }
          
          // 相同优先级按时间倒序
          return parseTime(b) - parseTime(a)
        })
      
      case 'pinned_desc':
        return sorted.sort((a, b) => {
          const pinnedA = a.isPinned || false
          const pinnedB = b.isPinned || false
          
          if (pinnedA !== pinnedB) return pinnedB - pinnedA
          
          // 置顶相同时按时间倒序
          return parseTime(b) - parseTime(a)
        })
      
      case 'views_desc':
        return sorted.sort((a, b) => {
          const viewsA = a.viewCount || 0
          const viewsB = b.viewCount || 0
          
          if (viewsA !== viewsB) return viewsB - viewsA
          
          // 浏览量相同按时间倒序
          return parseTime(b) - parseTime(a)
        })
      
      case 'title_asc':
        return sorted.sort((a, b) => {
          const titleA = (a.title || '').toLowerCase()
          const titleB = (b.title || '').toLowerCase()
          
          const result = titleA.localeCompare(titleB, 'zh-CN')
          if (result !== 0) return result
          
          // 标题相同按时间倒序
          return parseTime(b) - parseTime(a)
        })
      
      default:
        console.warn('未知排序类型:', sortType)
        return sorted
    }
  },

  // 排序菜单控制
  toggleSortMenu() {
    this.setData({
      showSortMenu: !this.data.showSortMenu
    })
  },

  hideSortMenu() {
    this.setData({
      showSortMenu: false
    })
  },

  // 切换排序方式
  onSortChange(e) {
    const sortType = e.currentTarget.dataset.sort
    const sortOption = this.data.sortOptions.find(option => option.value === sortType)
    
    this.setData({
      currentSort: sortType,
      currentSortLabel: sortOption ? sortOption.label : '排序',
      showSortMenu: false
    })
    this.filterAnnouncements()
    
    // 显示排序提示
    wx.showToast({
      title: `已切换为${sortOption.label}`,
      icon: 'success',
      duration: 1500
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
  },

  // 更新收藏状态
  updateCollectionStatus() {
    const collectedAnnouncements = wx.getStorageSync('collectedAnnouncements') || []
    const collectedIds = new Set(collectedAnnouncements.map(item => item.id))
    
    const updatedAnnouncements = this.data.announcements.map(item => ({
      ...item,
      isCollected: collectedIds.has(item.id)
    }))
    
    this.setData({
      announcements: updatedAnnouncements
    })
  },
}); 