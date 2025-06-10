Page({
  data: {
    examType: '期末考试',
    exams: []
  },

  onLoad() {
    this.loadExams();
  },

  loadExams() {
    // 模拟数据，实际项目中应该从后端API获取
    this.setData({
      exams: [
        {
          id: 1,
          courseName: '高等数学',
          date: '2024-01-15',
          time: '09:00-11:00',
          location: '教学楼A101'
        },
        {
          id: 2,
          courseName: '大学英语',
          date: '2024-01-16',
          time: '14:30-16:30',
          location: '教学楼B203'
        },
        {
          id: 3,
          courseName: '程序设计基础',
          date: '2024-01-17',
          time: '09:00-11:00',
          location: '教学楼C305'
        }
      ]
    });
  }
}); 