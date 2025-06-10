Page({
  data: {
    announcements: []
  },

  onLoad() {
    // 模拟数据，实际项目中应该从后端API获取
    this.setData({
      announcements: [
        {
          id: 1,
          title: '关于2024年寒假放假安排的通知',
          date: '2024-01-10'
        },
        {
          id: 2,
          title: '2024年春季学期选课通知',
          date: '2024-01-08'
        }
      ]
    });
  }
}); 