Page({
  data: {
    currentYear: 2024,
    currentMonth: 1,
    events: []
  },

  onLoad() {
    this.setCurrentDate();
    this.loadEvents();
  },

  setCurrentDate() {
    const now = new Date();
    this.setData({
      currentYear: now.getFullYear(),
      currentMonth: now.getMonth() + 1
    });
  },

  loadEvents() {
    // 模拟数据，实际项目中应该从后端API获取
    this.setData({
      events: [
        {
          id: 1,
          title: '2024年春季开学典礼',
          date: '2024-02-26',
          time: '09:00',
          location: '体育馆'
        },
        {
          id: 2,
          title: '校园歌手大赛初赛',
          date: '2024-02-28',
          time: '19:00',
          location: '学生活动中心'
        },
        {
          id: 3,
          title: '创新创业讲座',
          date: '2024-03-01',
          time: '14:30',
          location: '图书馆报告厅'
        }
      ]
    });
  }
}); 