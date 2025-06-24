const app = getApp()
const API = require('../../utils/api.js')

Page({
  data: {
    activeTab: 'borrow',
    searchKeyword: '',
    currentBorrow: 0,
    maxBorrow: 10,
    borrowList: [],
    borrowHistory: [],
    floors: [],
    popularBooks: [],
    newArrivals: [],
    overdueBooksCount: 0,
    currentReservation: null,
    recommendInfo: '',
    loading: false,
    searchResults: [],
    showSearchResults: false,
    todayCheckInCount: 156, // 今日进馆人数
    availableSeats: 234,    // 可用座位数
    totalSeats: 300,        // 总座位数
    announcements: [
      {
        id: 1,
        title: '图书馆闭馆通知',
        content: '因系统维护，本周六图书馆暂停开放',
        date: '2024-06-20'
      }
    ]
  },

  onLoad() {
    console.log('[图书馆] 📚 页面加载')
    this.loadAllData()
  },

  onShow() {
    console.log('[图书馆] 页面显示')
    this.refreshBorrowInfo()
  },

  // 加载所有数据
  loadAllData() {
    this.loadBorrowInfo()
    this.loadSeatInfo()
    this.loadPopularBooks()
    this.loadNewArrivals()
    this.loadBorrowHistory()
    this.checkOverdueBooks()
  },

  // 标签页切换
  onTabChange(e) {
    const tabValue = e.detail.value
    console.log('[图书馆] 🏷️ 切换标签:', tabValue)
    this.setData({
      activeTab: tabValue,
      showSearchResults: false
    })
    
    // 根据不同标签页加载相应数据
    if (tabValue === 'search' && this.data.popularBooks.length === 0) {
      this.loadPopularBooks()
    }
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({
      searchKeyword: e.detail.value
    })
    
    // 实时搜索建议
    if (e.detail.value.trim()) {
      this.searchBooks(e.detail.value.trim(), true)
    } else {
      this.setData({
        showSearchResults: false,
        searchResults: []
      })
    }
  },

  // 搜索提交
  onSearch() {
    if (!this.data.searchKeyword.trim()) {
      wx.showToast({
        title: '请输入搜索关键词',
        icon: 'none'
      })
      return
    }
    
    this.searchBooks(this.data.searchKeyword.trim(), false)
  },

  // 搜索图书
  async searchBooks(keyword, isRealTime = false) {
    console.log('[图书馆] 🔍 搜索图书:', keyword)
    
    if (!isRealTime) {
      this.setData({ loading: true })
    }
    
    try {
      const response = await API.searchBooks({
        keyword: keyword,
        page: 1,
        size: 10
      })
      
      if (response.code === 0) {
        const books = response.data.books || []
      this.setData({
          searchResults: books,
        showSearchResults: true,
        loading: false
      })
      
      if (!isRealTime) {
        wx.showToast({
            title: `找到${books.length}本相关图书`,
          icon: 'success'
        })
      }
      } else {
        throw new Error(response.message || '搜索失败')
      }
    } catch (error) {
      console.error('[图书馆] ❌ 搜索图书失败:', error)
      this.setData({ loading: false })
      
      if (!isRealTime) {
        wx.showToast({
          title: '搜索失败，请重试',
          icon: 'none'
        })
      }
    }
  },

  // 加载借阅信息
  async loadBorrowInfo() {
    this.setData({ loading: true })
    
    try {
      const response = await API.getBorrowRecords({
        status: 'borrowed',
        page: 1,
        size: 20
      })
      
      if (response.code === 0) {
        const borrowList = response.data.borrow_records || []
        const statistics = response.data.statistics || {}
      
      this.setData({
          currentBorrow: statistics.total_borrowed || borrowList.length,
        maxBorrow: 10,
          borrowList: borrowList,
        loading: false
      })
      } else {
        throw new Error(response.message || '获取借阅信息失败')
      }
    } catch (error) {
      console.error('[图书馆] ❌ 加载借阅信息失败:', error)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none'
      })
    }
  },

  // 加载座位信息
  async loadSeatInfo() {
    try {
      const response = await API.getSeatInfo()
      
      if (response.code === 0) {
        const areas = response.data.areas || []
        const statistics = response.data.statistics || {}
    
    this.setData({
          floors: areas,
          availableSeats: statistics.available_seats || 0,
          totalSeats: statistics.total_seats || 0
        })
      } else {
        throw new Error(response.message || '获取座位信息失败')
      }
    } catch (error) {
      console.error('[图书馆] ❌ 加载座位信息失败:', error)
      wx.showToast({
        title: '座位信息加载失败',
        icon: 'none'
      })
    }
  },

  // 加载热门图书
  async loadPopularBooks() {
    try {
      const response = await API.searchBooks({
        keyword: '',
        category: 'popular',
        page: 1,
        size: 6
      })
      
      if (response.code === 0) {
        const books = response.data.books || []
        this.setData({
          popularBooks: books
        })
      } else {
        throw new Error(response.message || '获取热门图书失败')
      }
    } catch (error) {
      console.error('[图书馆] ❌ 加载热门图书失败:', error)
    }
  },

  // 加载新书推荐
  async loadNewArrivals() {
    try {
      const response = await API.searchBooks({
        keyword: '',
        category: 'new',
        page: 1,
        size: 6
      })
      
      if (response.code === 0) {
        const books = response.data.books || []
    this.setData({
          newArrivals: books
        })
      } else {
        throw new Error(response.message || '获取新书推荐失败')
      }
    } catch (error) {
      console.error('[图书馆] ❌ 加载新书推荐失败:', error)
    }
  },

  // 加载借阅历史
  async loadBorrowHistory() {
    try {
      const response = await API.getBorrowRecords({
        status: 'returned',
        page: 1,
        size: 10
      })
      
      if (response.code === 0) {
        const borrowHistory = response.data.borrow_records || []
    this.setData({
          borrowHistory: borrowHistory
    })
      } else {
        throw new Error(response.message || '获取借阅历史失败')
      }
    } catch (error) {
      console.error('[图书馆] ❌ 加载借阅历史失败:', error)
    }
  },

  // 检查逾期图书
  checkOverdueBooks() {
    const overdueCount = this.data.borrowList.filter(book => book.status === 'overdue').length
    
    this.setData({
      overdueBooksCount: overdueCount
    })
    
    if (overdueCount > 0) {
      wx.showModal({
        title: '📚 逾期提醒',
        content: `您有${overdueCount}本图书已逾期，请尽快归还以免产生罚金。`,
        showCancel: true,
        cancelText: '稍后处理',
        confirmText: '查看详情',
        confirmColor: '#e34d59',
        success: (res) => {
          if (res.confirm) {
            this.setData({ activeTab: 'borrow' })
          }
        }
      })
    }
  },

  // 刷新借阅信息
  refreshBorrowInfo() {
    this.loadBorrowInfo()
    this.checkOverdueBooks()
  },

  // 续借图书
  async renewBook(e) {
    const book = e.currentTarget.dataset.book
    
    if (book.renewal_count >= book.max_renewals) {
      wx.showToast({
        title: '已达最大续借次数',
        icon: 'none'
      })
      return
    }
    
    wx.showModal({
      title: '续借确认',
      content: `确定要续借《${book.book_title}》吗？\n续借后到期日期将延长30天`,
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '续借中...' })
          
          try {
            const response = await API.renewBook(book.record_id)
            
            if (response.code === 0) {
            wx.hideLoading()
            wx.showToast({
              title: '续借成功',
              icon: 'success'
            })
            this.loadBorrowInfo()
            } else {
              throw new Error(response.message || '续借失败')
            }
          } catch (error) {
            console.error('[图书馆] ❌ 续借失败:', error)
            wx.hideLoading()
            wx.showToast({
              title: '续借失败，请重试',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  // 查看图书详情
  onViewBookDetail(e) {
    const book = e.currentTarget.dataset.book
    console.log('[图书馆] 📖 查看图书详情:', book.title || book.book_title)
    
    // 存储图书信息到全局数据
    app.globalData.currentBook = book
    
    wx.navigateTo({
      url: '/pages/library/book-detail/book-detail'
    })
  },

  // 预约图书
  async reserveBook(e) {
    const book = e.currentTarget.dataset.book
    
    if (book.status === 'available') {
      wx.showToast({
        title: '该图书可直接借阅',
        icon: 'none'
      })
      return
    }
    
    wx.showModal({
      title: '预约图书',
      content: `确定要预约《${book.title}》吗？\n图书归还后将优先为您保留3天`,
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '预约中...' })
          
          try {
            const response = await API.borrowBook(book.book_id)
            
            if (response.code === 0) {
            wx.hideLoading()
            wx.showToast({
              title: '预约成功',
              icon: 'success'
            })
            } else {
              throw new Error(response.message || '预约失败')
            }
          } catch (error) {
            console.error('[图书馆] ❌ 预约失败:', error)
            wx.hideLoading()
            wx.showToast({
              title: '预约失败，请重试',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  // 选择楼层
  onSelectFloor(e) {
    const floor = e.currentTarget.dataset.floor
    console.log('[图书馆] 🏢 选择楼层:', floor.area)
    
    wx.navigateTo({
      url: `/pages/library/seat-map/seat-map?floorId=${floor.floor}&floorName=${floor.area}`
    })
  },

  // 图书推荐
  onRecommendInput(e) {
    this.setData({
      recommendInfo: e.detail.value
    })
  },

  onRecommend() {
    if (!this.data.recommendInfo.trim()) {
      wx.showToast({
        title: '请输入图书信息',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '荐购确认',
      content: `确定要推荐购买以下图书吗？\n\n${this.data.recommendInfo}`,
      success: (res) => {
        if (res.confirm) {
          wx.showToast({
            title: '荐购提交成功',
            icon: 'success'
          })

          this.setData({
            recommendInfo: ''
          })
        }
      }
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    console.log('[图书馆] 🔄 下拉刷新')
    this.loadAllData()
    
    setTimeout(() => {
      wx.stopPullDownRefresh()
      wx.showToast({
        title: '刷新完成',
        icon: 'success'
      })
    }, 1500)
  },

  // 返回上一页
  onBack() {
    wx.navigateBack()
  }
}) 