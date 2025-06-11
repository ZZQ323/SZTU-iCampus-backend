Page({
  data: {
    notices: []
  },

  onLoad() {
    this.loadNotices();
  },

  onBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  viewNotice(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/notices/detail?id=${id}`
    });
  },

  loadNotices() {
    // TODO: 从后端API获取通知列表
    this.setData({
      notices: [
        {
          id: 1,
          title: '关于2024年春季学期开学安排的通知',
          department: '教务处',
          date: '2024-02-20'
        },
        {
          id: 2,
          title: '关于开展2024年学生创新项目申报的通知',
          department: '学生处',
          date: '2024-02-19'
        }
      ]
    });
  }
}); 