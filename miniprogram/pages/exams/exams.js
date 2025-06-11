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
    countdown: ''
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
    // TODO: 从后端获取考试数据
    // 模拟数据
    const mockExams = [
      {
        id: 1,
        courseName: '高等数学',
        time: '2024-01-15 14:30-16:30',
        location: '教学楼A101'
      },
      {
        id: 2,
        courseName: '大学英语',
        time: '2024-01-16 09:00-11:00',
        location: '教学楼B203'
      }
    ];

    const nextExam = mockExams[0];
    this.setData({
      exams: mockExams,
      nextExam
    });

    this.startCountdown(nextExam.time);
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