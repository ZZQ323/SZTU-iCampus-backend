Page({
  data: {
    currentSemester: '2023-2024-2',
    semesters: [
      { label: '2023-2024-2', value: '2023-2024-2' },
      { label: '2023-2024-1', value: '2023-2024-1' },
      { label: '2022-2023-2', value: '2022-2023-2' },
      { label: '2022-2023-1', value: '2022-2023-1' }
    ],
    grades: [],
    gpa: '0.00',
    totalCredits: '0'
  },

  onLoad() {
    this.loadGrades();
  },

  onBack() {
    wx.navigateBack();
  },

  onSemesterChange(e) {
    const { value } = e.detail;
    this.setData({
      currentSemester: value;
    });
    this.loadGrades();
  },

  loadGrades() {
    // TODO: 从后端获取成绩数据
    // 模拟数据
    const mockGrades = [
      {
        id: 1,
        courseName: '高等数学',
        credits: 4,
        grade: 'A'
      },
      {
        id: 2,
        courseName: '大学英语',
        credits: 3,
        grade: 'B+'
      }
    ];

    // 计算GPA和总学分
    const totalCredits = mockGrades.reduce((sum, course) => sum + course.credits, 0);
    const gpa = (mockGrades.reduce((sum, course) => {
      const gradePoint = this.calculateGradePoint(course.grade);
      return sum + gradePoint * course.credits;
    }, 0) / totalCredits).toFixed(2);

    this.setData({
      grades: mockGrades,
      gpa,
      totalCredits
    });
  },

  calculateGradePoint(grade) {
    if (grade === 'A') return 4.0;
    if (grade === 'B+') return 3.7;
    if (grade === 'B') return 3.3;
    if (grade === 'C+') return 2.3;
    if (grade === 'C') return 2.0;
    if (grade === 'D+') return 1.3;
    if (grade === 'D') return 1.0;
    return 0.0;
  },

  onViewDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/grades/detail/detail?id=${id}`
    });
  }
}); 