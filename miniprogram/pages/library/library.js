const app = getApp()

Page({
  data: {
    activeTab: 'borrow',
    searchKeyword: '',
    currentBorrow: 0,
    maxBorrow: 10,
    borrowList: [],
    floors: [],
    currentReservation: null,
    recommendInfo: '',
    loading: false
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

    wx.navigateTo({
      url: `/pages/library/search/search?keyword=${this.data.searchKeyword}`
    })
  },

  loadBorrowInfo() {
    this.setData({ loading: true });
    
    const userInfo = wx.getStorageSync('userInfo');
    const studentId = userInfo?.studentId || '2024001';
    
    wx.request({
      url: `${app.globalData.baseURL}/api/v1/library/borrow-info`,
      method: 'GET',
      data: {
        student_id: studentId
      },
      success: (res) => {
        console.log('[图书馆] 借阅信息API响应:', res);
        
        if (res.statusCode === 200 && res.data.code === 0) {
          const borrowData = res.data.data;
          
          this.setData({
            currentBorrow: borrowData.current_borrow,
            maxBorrow: borrowData.max_borrow,
            borrowList: borrowData.borrow_list,
            loading: false
          });
        } else {
          console.error('[图书馆] 获取借阅信息失败:', res.data);
          this.setData({ loading: false });
        }
      },
      fail: (error) => {
        console.error('[图书馆] 借阅信息请求失败:', error);
        this.setData({ loading: false });
      }
    });
  },

  loadSeatInfo() {
    wx.request({
      url: `${app.globalData.baseURL}/api/v1/library/seats`,
      method: 'GET',
      success: (res) => {
        console.log('[图书馆] 座位信息API响应:', res);
        
        if (res.statusCode === 200 && res.data.code === 0) {
          this.setData({
            floors: res.data.data.floors
          });
        } else {
          console.error('[图书馆] 获取座位信息失败:', res.data);
        }
      },
      fail: (error) => {
        console.error('[图书馆] 座位信息请求失败:', error);
      }
    });
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

    wx.showToast({
      title: '荐购成功',
      icon: 'success'
    })

    this.setData({
      recommendInfo: ''
    })
  }
}) 