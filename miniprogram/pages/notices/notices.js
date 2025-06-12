const app = getApp()

Page({
  data: {
    notices: [],
    loading: true,
    error: '',
    departments: ['全部', '教务处', '图书馆', '信息中心', '学生事务中心', '后勤服务中心'],
    selectedDept: '全部',
    noticeTypes: ['全部', '紧急通知', '普通通知', '信息通知'],
    selectedType: '全部'
  },

  onLoad() {
    this.loadNotices();
  },

  onBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  loadNotices() {
    this.setData({ loading: true, error: '' });
    
    // 构建请求参数
    let url = `${app.globalData.baseUrl}/api/notices?limit=50`;
    
    if (this.data.selectedDept !== '全部') {
      url += `&department=${encodeURIComponent(this.data.selectedDept)}`;
    }
    
    if (this.data.selectedType !== '全部') {
      const typeMap = {
        '紧急通知': 'urgent',
        '普通通知': 'normal', 
        '信息通知': 'info'
      };
      url += `&notice_type=${typeMap[this.data.selectedType]}`;
    }

    wx.request({
      url: url,
      method: 'GET',
      success: (res) => {
        console.log('通知API响应:', res.data);
        if (res.statusCode === 200 && res.data.code === 0) {
          this.setData({
            notices: res.data.data.notices || [],
            loading: false
          });
        } else {
          console.error('获取通知失败:', res.data);
          this.setData({
            error: '获取通知失败，请稍后重试',
            loading: false
          });
        }
      },
      fail: (err) => {
        console.error('请求通知失败:', err);
        this.setData({
          error: '网络请求失败，请检查网络连接',
          loading: false
        });
      }
    });
  },

  onPullDownRefresh() {
    this.loadNotices();
    setTimeout(() => {
      wx.stopPullDownRefresh();
    }, 1000);
  },

  onDeptChange(e) {
    const dept = this.data.departments[e.detail.value];
    this.setData({
      selectedDept: dept
    });
    this.loadNotices();
  },

  onTypeChange(e) {
    const type = this.data.noticeTypes[e.detail.value];
    this.setData({
      selectedType: type
    });
    this.loadNotices();
  },

  viewNotice(e) {
    const { id, title, content, department, priority, notice_type } = e.currentTarget.dataset;
    
    // 显示通知详情
    wx.showModal({
      title: title,
      content: content,
      showCancel: true,
      cancelText: '关闭',
      confirmText: '已读',
      success: (res) => {
        if (res.confirm) {
          console.log('用户点击已读');
          // TODO: 可以在这里标记通知为已读
        }
      }
    });
  },

  getPriorityColor(priority) {
    const colors = {
      'high': '#ff4757',
      'medium': '#ffa502', 
      'low': '#2ed573'
    };
    return colors[priority] || '#666';
  },

  getTypeText(type) {
    const texts = {
      'urgent': '紧急',
      'normal': '普通',
      'info': '信息'
    };
    return texts[type] || '普通';
  }
}); 