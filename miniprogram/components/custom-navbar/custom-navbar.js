Component({
  properties: {
    title: {
      type: String,
      value: ''
    },
    showBack: {
      type: Boolean,
      value: true
    },
    background: {
      type: String,
      value: '#4a90e2'
    },
    color: {
      type: String,
      value: '#ffffff'
    }
  },

  data: {
    statusBarHeight: 0,
    navBarHeight: 44,
    menuButtonInfo: null
  },

  lifetimes: {
    attached() {
      const systemInfo = wx.getSystemInfoSync()
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect()
      
      this.setData({
        statusBarHeight: systemInfo.statusBarHeight,
        menuButtonInfo: menuButtonInfo,
        navBarHeight: (menuButtonInfo.top - systemInfo.statusBarHeight) * 2 + menuButtonInfo.height
      })
    }
  },

  methods: {
    onBack() {
      if (this.data.showBack) {
        wx.navigateBack({
          delta: 1,
          fail: () => {
            wx.switchTab({
              url: '/pages/index/index'
            })
          }
        })
      }
    }
  }
}) 