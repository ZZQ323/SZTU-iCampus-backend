const app = getApp()

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
  searchBooks(keyword, isRealTime = false) {
    console.log('[图书馆] 🔍 搜索图书:', keyword)
    
    if (!isRealTime) {
      this.setData({ loading: true })
    }
    
    // 模拟搜索结果
    const mockResults = [
      {
        id: 1,
        title: `《${keyword}相关图书》`,
        author: '著名作者',
        isbn: '978-7-111-12345-6',
        location: 'A区3楼 A301.2',
        status: 'available',
        borrowCount: 156,
        rating: 4.5,
        cover: '/assets/test/book1.jpg'
      },
      {
        id: 2,
        title: `《高级${keyword}教程》`,
        author: '专业团队',
        isbn: '978-7-222-54321-8',
        location: 'B区2楼 B205.1',
        status: 'borrowed',
        borrowCount: 89,
        rating: 4.2,
        cover: '/assets/test/book2.jpg'
      },
      {
        id: 3,
        title: `《${keyword}实践指南》`,
        author: '实战专家',
        isbn: '978-7-333-98765-4',
        location: 'A区1楼 A102.5',
        status: 'available',
        borrowCount: 234,
        rating: 4.8,
        cover: '/assets/test/book3.jpg'
      }
    ]
    
    setTimeout(() => {
      this.setData({
        searchResults: mockResults,
        showSearchResults: true,
        loading: false
      })
      
      if (!isRealTime) {
        wx.showToast({
          title: `找到${mockResults.length}本相关图书`,
          icon: 'success'
        })
      }
    }, isRealTime ? 200 : 800)
  },

  // 加载借阅信息
  loadBorrowInfo() {
    this.setData({ loading: true })
    
    const userInfo = wx.getStorageSync('userInfo')
    const studentId = userInfo?.studentId || '2024001'
    
    // 模拟API请求
    setTimeout(() => {
      const mockBorrowList = [
        {
          id: 1,
          title: '《计算机网络原理》',
          author: '谢希仁',
          isbn: '978-7-111-31570-8',
          borrowDate: '2024-05-15',
          dueDate: '2024-06-15',
          renewCount: 0,
          maxRenew: 2,
          isOverdue: false,
          daysLeft: 5,
          location: 'A区3楼 A301.2',
          cover: '/assets/test/book1.jpg'
        },
        {
          id: 2,
          title: '《数据结构与算法》',
          author: '严蔚敏',
          isbn: '978-7-302-25737-2',
          borrowDate: '2024-05-10',
          dueDate: '2024-06-10',
          renewCount: 1,
          maxRenew: 2,
          isOverdue: true,
          daysLeft: -3,
          location: 'B区2楼 B205.1',
          cover: '/assets/test/book2.jpg'
        }
      ]
      
      this.setData({
        currentBorrow: mockBorrowList.length,
        maxBorrow: 10,
        borrowList: mockBorrowList,
        loading: false
      })
    }, 1000)
  },

  // 加载座位信息
  loadSeatInfo() {
    // 模拟座位数据
    const mockFloors = [
      {
        id: 1,
        name: '一楼阅览区',
        totalSeats: 80,
        availableSeats: 23,
        occupancyRate: 71,
        description: '期刊阅览、报纸阅读'
      },
      {
        id: 2,
        name: '二楼学习区',
        totalSeats: 120,
        availableSeats: 45,
        occupancyRate: 63,
        description: '安静学习、个人研修'
      },
      {
        id: 3,
        name: '三楼研讨区',
        totalSeats: 60,
        availableSeats: 18,
        occupancyRate: 70,
        description: '小组讨论、团队学习'
      },
      {
        id: 4,
        name: '四楼电子阅览室',
        totalSeats: 40,
        availableSeats: 12,
        occupancyRate: 70,
        description: '电子资源、网络检索'
      }
    ]
    
    this.setData({
      floors: mockFloors,
      availableSeats: mockFloors.reduce((sum, floor) => sum + floor.availableSeats, 0),
      totalSeats: mockFloors.reduce((sum, floor) => sum + floor.totalSeats, 0)
    })
  },

  // 加载热门图书
  loadPopularBooks() {
    const mockPopularBooks = [
      {
        id: 1,
        title: '《深度学习》',
        author: 'Ian Goodfellow',
        borrowCount: 342,
        rating: 4.8,
        status: 'available',
        cover: '/assets/test/book1.jpg'
      },
      {
        id: 2,
        title: '《算法导论》',
        author: 'Thomas H. Cormen',
        borrowCount: 298,
        rating: 4.7,
        status: 'borrowed',
        cover: '/assets/test/book2.jpg'
      },
      {
        id: 3,
        title: '《设计模式》',
        author: 'Erich Gamma',
        borrowCount: 245,
        rating: 4.6,
        status: 'available',
        cover: '/assets/test/book3.jpg'
      }
    ]
    
    this.setData({
      popularBooks: mockPopularBooks
    })
  },

  // 加载新书推荐
  loadNewArrivals() {
    const mockNewArrivals = [
      {
        id: 4,
        title: '《机器学习实战》',
        author: '周志华',
        arrivalDate: '2024-06-18',
        status: 'available',
        cover: '/assets/test/book4.jpg'
      },
      {
        id: 5,
        title: '《Python编程从入门到精通》',
        author: '李华',
        arrivalDate: '2024-06-15',
        status: 'available',
        cover: '/assets/test/book5.jpg'
      }
    ]
    
    this.setData({
      newArrivals: mockNewArrivals
    })
  },

  // 加载借阅历史
  loadBorrowHistory() {
    const mockHistory = [
      {
        id: 1,
        title: '《操作系统概念》',
        author: 'Abraham Silberschatz',
        borrowDate: '2024-04-01',
        returnDate: '2024-04-30',
        rating: 5
      },
      {
        id: 2,
        title: '《编译原理》',
        author: 'Alfred V. Aho',
        borrowDate: '2024-03-15',
        returnDate: '2024-04-10',
        rating: 4
      }
    ]
    
    this.setData({
      borrowHistory: mockHistory
    })
  },

  // 检查逾期图书
  checkOverdueBooks() {
    const overdueCount = this.data.borrowList.filter(book => book.isOverdue).length
    
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
  renewBook(e) {
    const book = e.currentTarget.dataset.book
    
    if (book.renewCount >= book.maxRenew) {
      wx.showToast({
        title: '已达最大续借次数',
        icon: 'none'
      })
      return
    }
    
    wx.showModal({
      title: '续借确认',
      content: `确定要续借《${book.title}》吗？\n续借后到期日期将延长30天`,
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '续借中...' })
          
          setTimeout(() => {
            wx.hideLoading()
            wx.showToast({
              title: '续借成功',
              icon: 'success'
            })
            this.loadBorrowInfo()
          }, 1500)
        }
      }
    })
  },

  // 查看图书详情
  onViewBookDetail(e) {
    const book = e.currentTarget.dataset.book
    console.log('[图书馆] 📖 查看图书详情:', book.title)
    
    // 存储图书信息到全局数据
    app.globalData.currentBook = book
    
    wx.navigateTo({
      url: '/pages/library/book-detail/book-detail'
    })
  },

  // 预约图书
  reserveBook(e) {
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
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '预约中...' })
          
          setTimeout(() => {
            wx.hideLoading()
            wx.showToast({
              title: '预约成功',
              icon: 'success'
            })
          }, 1000)
        }
      }
    })
  },

  // 选择楼层
  onSelectFloor(e) {
    const floor = e.currentTarget.dataset.floor
    console.log('[图书馆] 🏢 选择楼层:', floor.name)
    
    wx.navigateTo({
      url: `/pages/library/seat-map/seat-map?floorId=${floor.id}&floorName=${floor.name}`
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