Page({
  data: {
    currentYear: 2024,
    currentMonth: 1,
    calendarVisible: false,
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

  onBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  onDateSelect(e) {
    const { value } = e.detail;
    this.setData({
      calendarVisible: false
    });
    // TODO: 根据选择的日期筛选活动
  },

  onCalendarClose() {
    this.setData({
      calendarVisible: false
    });
  },

  viewEvent(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/events/detail?id=${id}`
    });
  },

  loadEvents() {
    // TODO: 从后端API获取活动列表
    this.setData({
      events: [
        {
          id: 1,
          title: '2024年春季开学典礼',
          time: '2024-02-26 09:00',
          location: '体育馆'
        },
        {
          id: 2,
          title: '创新创业大赛启动仪式',
          time: '2024-02-28 14:30',
          location: '图书馆报告厅'
        }
      ]
    });
  }
}); 