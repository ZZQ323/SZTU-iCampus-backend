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
      // 使用新的API替代已弃用的getSystemInfoSync
      let statusBarHeight = 0;
      try {
        const windowInfo = wx.getWindowInfo();
        statusBarHeight = windowInfo.statusBarHeight || 0;
      } catch (e) {
        // 兼容旧版本
        try {
          const systemInfo = wx.getSystemInfoSync();
          statusBarHeight = systemInfo.statusBarHeight || 0;
        } catch (err) {
          console.warn('获取系统信息失败', err);
          statusBarHeight = 44; // 默认值
        }
      }
      
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect()
      
      this.setData({
        statusBarHeight: statusBarHeight,
        menuButtonInfo: menuButtonInfo,
        navBarHeight: (menuButtonInfo.top - statusBarHeight) * 2 + menuButtonInfo.height
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