const app = getApp()

Page({
  data: {},

  onLoad() {
    console.log('[通讯录] 页面加载')
  },

  onShow() {
    console.log('[通讯录] 页面显示')
  },

  onPullDownRefresh() {
    wx.stopPullDownRefresh()
  }
}) 