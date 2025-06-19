const app = getApp()

Page({
  data: {
    currentType: 'final',
    examTypes: [
      { label: '期末考试', value: 'final' },
      { label: '期中考试', value: 'midterm' },
      { label: '补考', value: 'makeup' }
    ],
    exams: [],
    nextExam: null,
    countdown: '',
    loading: true
  },

  onLoad() {
    this.loadExams();
  },

  onUnload() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
    }
  },

  onBack() {
    wx.navigateBack();
  },

  onTypeChange(e) {
    const { value } = e.detail;
    this.setData({
      currentType: value
    });
    this.loadExams();
  },

  loadExams() {
    this.setData({ loading: true });
    
    const userInfo = wx.getStorageSync('userInfo');
    const studentId = userInfo?.studentId || '2024001';
    
    wx.request({
      url: `${app.globalData.baseURL}/api/v1/exams/`,
      method: 'GET',
      data: {
        student_id: studentId,
        exam_type: this.data.currentType
      },
      success: (res) => {
        console.log('[考试] API响应:', res);
        
        if (res.statusCode === 200 && res.data.code === 0) {
          const { exams, next_exam } = res.data.data;
          
          this.setData({
            exams: exams,
            nextExam: next_exam,
            loading: false
          });
          
          if (next_exam) {
            this.startCountdown(`${next_exam.exam_date} ${next_exam.start_time}`);
          }
          
          wx.showToast({
            title: `加载${exams.length}门考试`,
            icon: 'success'
          });
        } else {
          console.error('[考试] 获取失败:', res.data);
          this.setData({ loading: false });
          wx.showToast({
            title: '获取考试信息失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        console.error('[考试] 请求失败:', error);
        this.setData({ loading: false });
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },

  startCountdown(examTime) {
    const updateCountdown = () => {
      const now = new Date();
      const exam = new Date(examTime);
      const diff = exam - now;

      if (diff <= 0) {
        this.setData({ countdown: '考试已开始' });
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      this.setData({
        countdown: `${days}天${hours}小时${minutes}分${seconds}秒`
      });
    };

    updateCountdown();
    this.countdownTimer = setInterval(updateCountdown, 1000);
  },

  onViewDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/exams/detail/detail?id=${id}`
    });
  }
}); 