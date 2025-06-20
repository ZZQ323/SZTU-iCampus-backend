App({
  globalData: {
    userInfo: null,
    baseURL: 'http://localhost:8000'
  },
  
  onLaunch() {
    // 检查更新
    if (wx.canIUse('getUpdateManager')) {
      const updateManager = wx.getUpdateManager()
      updateManager.onCheckForUpdate(function (res) {
        if (res.hasUpdate) {
          updateManager.onUpdateReady(function () {
            wx.showModal({
              title: '更新提示',
              content: '新版本已经准备好，是否重启应用？',
              success: function (res) {
                if (res.confirm) {
                  updateManager.applyUpdate()
                }
              }
            })
          })
        }
      })
    }

    // 获取系统信息
    wx.getWindowInfo({
      success: e => {
        this.globalData.StatusBar = e.statusBarHeight
      }
    })
    
    wx.getDeviceInfo({
      success: e => {
        this.globalData.CustomBar = e.platform == 'android' ? this.globalData.StatusBar + 50 : this.globalData.StatusBar + 45
      }
    })
  }
}) 