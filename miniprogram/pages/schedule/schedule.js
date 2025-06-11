Page({
  data: {
    currentWeek: 1,
    visible: false,
    schedules: []
  },

  onLoad() {
    // 计算当前周次
    this.calculateCurrentWeek();
  },

  calculateCurrentWeek() {
    // 这里应该根据学期开始时间计算当前周次
    // 暂时使用模拟数据
    this.setData({
      currentWeek: 1
    });
  },

  onBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  onConfirm(e) {
    const { value } = e.detail;
    // 处理日期选择
    this.setData({
      visible: false
    });
    // TODO: 根据选择的日期获取课表数据
  },

  onClose() {
    this.setData({
      visible: false
    });
  }
}); 