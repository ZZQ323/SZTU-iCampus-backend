Page({
  data: {
    currentWeek: 1
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
  }
}); 