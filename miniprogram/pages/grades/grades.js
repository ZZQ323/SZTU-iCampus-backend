Page({
  data: {
    currentSemester: '2023-2024学年第二学期',
    grades: [],
    gpa: '3.85',
    totalCredits: '24'
  },

  onLoad() {
    this.loadGrades();
  },

  loadGrades() {
    // 模拟数据，实际项目中应该从后端API获取
    this.setData({
      grades: [
        {
          id: 1,
          courseName: '高等数学',
          credit: 4,
          score: 85,
          gradePoint: '3.5'
        },
        {
          id: 2,
          courseName: '大学英语',
          credit: 3,
          score: 92,
          gradePoint: '4.0'
        },
        {
          id: 3,
          courseName: '程序设计基础',
          credit: 4,
          score: 88,
          gradePoint: '3.7'
        },
        {
          id: 4,
          courseName: '大学物理',
          credit: 4,
          score: 78,
          gradePoint: '3.0'
        }
      ]
    });
  }
}); 