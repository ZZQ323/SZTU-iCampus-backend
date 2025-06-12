const app = getApp()

Page({
  data: {
    currentSemester: '全部',
    currentAcademicYear: '全部',
    semesters: ['全部', '2023-2024-1', '2023-2024-2', '2024-2025-1', '2024-2025-2'],
    academicYears: ['全部', '2023-2024', '2024-2025'],
    courseTypes: ['全部', '必修', '选修', '实践'],
    selectedCourseType: '全部',
    grades: [],
    loading: true,
    error: '',
    summary: {
      total_courses: 0,
      total_credits: 0,
      avg_score: 0,
      avg_gpa: 0,
      pass_rate: 0,
      student_id: '2024001'
    }
  },

  onLoad() {
    this.loadGrades();
  },

  onBack() {
    wx.navigateBack();
  },

  onSemesterChange(e) {
    const semester = this.data.semesters[e.detail.value];
    this.setData({
      currentSemester: semester
    });
    this.loadGrades();
  },

  onAcademicYearChange(e) {
    const year = this.data.academicYears[e.detail.value];
    this.setData({
      currentAcademicYear: year
    });
    this.loadGrades();
  },

  onCourseTypeChange(e) {
    const type = this.data.courseTypes[e.detail.value];
    this.setData({
      selectedCourseType: type
    });
    this.loadGrades();
  },

  loadGrades() {
    this.setData({ loading: true, error: '' });
    
    // 构建请求参数
    let url = `${app.globalData.baseUrl}/api/grades?limit=50`;
    
    if (this.data.currentSemester !== '全部') {
      url += `&semester=${encodeURIComponent(this.data.currentSemester)}`;
    }
    
    if (this.data.currentAcademicYear !== '全部') {
      url += `&academic_year=${encodeURIComponent(this.data.currentAcademicYear)}`;
    }
    
    if (this.data.selectedCourseType !== '全部') {
      url += `&course_type=${encodeURIComponent(this.data.selectedCourseType)}`;
    }

    wx.request({
      url: url,
      method: 'GET',
      success: (res) => {
        console.log('成绩API响应:', res.data);
        if (res.statusCode === 200 && res.data.code === 0) {
          this.setData({
            grades: res.data.data.grades || [],
            summary: res.data.data.summary || {},
            loading: false
          });
        } else {
          console.error('获取成绩失败:', res.data);
          this.setData({
            error: '获取成绩失败，请稍后重试',
            loading: false
          });
        }
      },
      fail: (err) => {
        console.error('请求成绩失败:', err);
        this.setData({
          error: '网络请求失败，请检查网络连接',
          loading: false
        });
      }
    });
  },

  onPullDownRefresh() {
    this.loadGrades();
    setTimeout(() => {
      wx.stopPullDownRefresh();
    }, 1000);
  },

  onViewDetail(e) {
    const { id, course_name, course_code, total_score, grade_level, teacher_name, semester, academic_year, regular_score, midterm_score, final_score, class_rank, class_total } = e.currentTarget.dataset;
    
    // 显示成绩详情
    wx.showModal({
      title: course_name,
      content: `课程代码：${course_code}\n学期：${semester}\n任课教师：${teacher_name}\n\n成绩详情：\n平时成绩：${regular_score || '无'}\n期中成绩：${midterm_score || '无'}\n期末成绩：${final_score || '无'}\n总成绩：${total_score}\n等级：${grade_level}\n\n班级排名：${class_rank}/${class_total}`,
      showCancel: false,
      confirmText: '知道了'
    });
  },

  getGradeColor(score) {
    if (score >= 90) return '#34c759';
    else if (score >= 80) return '#007aff';
    else if (score >= 70) return '#ff9500';
    else if (score >= 60) return '#ff3b30';
    else return '#8e8e93';
  },

  getLevelColor(level) {
    if (level && (level.includes('A') || level === 'A+')) return '#34c759';
    else if (level && level.includes('B')) return '#007aff';
    else if (level && level.includes('C')) return '#ff9500';
    else if (level && level.includes('D')) return '#ff3b30';
    else return '#8e8e93';
  }
}); 