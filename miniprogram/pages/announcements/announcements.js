const app = getApp()

// Page(options) options 是一个对象，属性会被直接挂到页面实例上

Page({
  data: {
    announcements: [],
    loading: true
  },
  onLoad() {
    // 参数 query 携带通过 ? 拼接的 URL 查询参数
    // 第一次加载执行一次
    this.fetchAnnouncements()
  },

  onShow() {
    // 页面显示时刷新数据
    // 页面每次可见时调用。常用来刷新 UI、重连 WebSocket 等
    this.fetchAnnouncements()
  },

  async fetchAnnouncements() {
    try {
      this.setData({ loading: true })

      const response = await new Promise((resolve, reject) => {
        // 小程序最底层 HTTP 请求。
        // wx.request({url, method, data, header, success, fail})
          // url 完整地址
          // method GET/POST/PUT…
          // header 额外请求头
          // success(res) 成功回调，res.statusCode 是 HTTP 码，res.data 是响应 JSON
          // fail(err) 网络层面错误（断网/超时）
        wx.request({
          url: `${app.globalData.baseUrl}/api/announcements`,
          method: 'GET',
          header: {
            'Content-Type': 'application/json'
          },
          success: resolve,
          fail: reject
        })
      })

      console.log('公告页API Response:', response)

      if (response.statusCode === 200 && response.data.code === 0) {
        this.setData({
          announcements: response.data.data.announcements || []
        })
        console.log('公告页数据已更新:', response.data.data.announcements)
      } else {
        console.error('API返回错误:', response.data)
        wx.showToast({
          title: '获取公告失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('获取公告失败:', error)
      wx.showToast({
        title: '网络连接失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.fetchAnnouncements().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onBack() {
    // delta 表示返回几层，1 = 上一页。
    wx.navigateBack({
      delta: 1
    });
  },

  viewAnnouncement(e) {
    const announcement = e.currentTarget.dataset.announcement
    // 将公告数据存储到全局，供详情页使用
    app.globalData.currentAnnouncement = announcement

    wx.showModal({
      title: announcement.title,
      content: announcement.content.length > 100 ?
        announcement.content.substring(0, 100) + '...' :
        announcement.content,
      showCancel: true,
      confirmText: '查看详情',
      cancelText: '关闭',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: `/pages/announcements/detail?id=${announcement.id}`
          })
        }
      }
    })
  }
}); 