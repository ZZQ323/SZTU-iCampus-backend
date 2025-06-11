Page({
  data: {
    activeTab: 'borrow',
    searchKeyword: '',
    currentBorrow: 0,
    maxBorrow: 10,
    borrowList: [],
    floors: [],
    currentReservation: null,
    recommendInfo: ''
  },

  onLoad() {
    this.loadBorrowInfo()
    this.loadSeatInfo()
  },

  onTabChange(e) {
    this.setData({
      activeTab: e.detail.value
    })
  },

  onSearchInput(e) {
    this.setData({
      searchKeyword: e.detail.value
    })
  },

  onSearch() {
    if (!this.data.searchKeyword.trim()) {
      wx.showToast({
        title: '请输入搜索关键词',
        icon: 'none'
      })
      return
    }

    // TODO: 调用搜索接口
    wx.navigateTo({
      url: `/pages/library/search/search?keyword=${this.data.searchKeyword}`
    })
  },

  loadBorrowInfo() {
    // TODO: 从后端获取借阅信息
    // 模拟数据
    this.setData({
      currentBorrow: 2,
      maxBorrow: 10,
      borrowList: [
        {
          id: 1,
          bookName: '高等数学（第七版）',
          borrowDate: '2024-03-01',
          returnDate: '2024-06-01'
        },
        {
          id: 2,
          bookName: '大学英语（第四版）',
          borrowDate: '2024-03-05',
          returnDate: '2024-06-05'
        }
      ]
    })
  },

  loadSeatInfo() {
    // TODO: 从后端获取座位信息
    // 模拟数据
    this.setData({
      floors: [
        {
          id: 1,
          name: '一楼阅览室',
          availableSeats: 45
        },
        {
          id: 2,
          name: '二楼阅览室',
          availableSeats: 38
        },
        {
          id: 3,
          name: '三楼阅览室',
          availableSeats: 52
        }
      ]
    })
  },

  onViewBookDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/library/book/book?id=${id}`
    })
  },

  onSelectFloor(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/library/seat/seat?floorId=${id}`
    })
  },

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

    // TODO: 调用荐购接口
    wx.showToast({
      title: '荐购成功',
      icon: 'success'
    })

    this.setData({
      recommendInfo: ''
    })
  }
}) 