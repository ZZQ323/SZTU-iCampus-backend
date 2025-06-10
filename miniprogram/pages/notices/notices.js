Page({
  data: {
    notices: []
  },

  onLoad() {
    // 模拟数据，实际项目中应该从后端API获取
    this.setData({
      notices: [
        {
          id: 1,
          title: '关于举办2024年创新创业大赛的通知',
          department: '创新创业学院',
          date: '2024-01-15'
        },
        {
          id: 2,
          title: '2024年春季学期学生社团招新通知',
          department: '学生处',
          date: '2024-01-12'
        },
        {
          id: 3,
          title: '关于开展2024年寒假社会实践活动的通知',
          department: '团委',
          date: '2024-01-10'
        }
      ]
    });
  }
}); 