const app = getApp()

Page({
  data: {
    gradesData: {
      semester_info: {
        current_semester: "2024-1",
        academic_year: "2024-2025"
      },
      summary: {
        total_courses: 8,
        total_credits: 24.5,
        avg_score: 87.3,
        gpa: 3.67,
        rank: 5,
        total_students: 35
      },
      grades: [
        {
          id: 1,
          course_name: "数据结构与算法",
          course_code: "CS001",
          credits: 4.0,
          teacher: "李教授",
          regular_score: 85,
          midterm_score: 88,
          final_score: 92,
          total_score: 90,
          grade_level: "A-",
          gpa_points: 3.7,
          course_type: "必修"
        },
        {
          id: 2,
          course_name: "软件工程",
          course_code: "CS002", 
          credits: 3.5,
          teacher: "王教授",
          regular_score: 90,
          midterm_score: 85,
          final_score: 88,
          total_score: 88,
          grade_level: "B+",
          gpa_points: 3.3,
          course_type: "必修"
        },
        {
          id: 3,
          course_name: "数据库原理", 
          course_code: "CS003",
          credits: 3.0,
          teacher: "张教授",
          regular_score: 88,
          midterm_score: 90,
          final_score: 85,
          total_score: 87,
          grade_level: "B+",
          gpa_points: 3.3,
          course_type: "必修"
        },
        {
          id: 4,
          course_name: "计算机网络",
          course_code: "CS004",
          credits: 3.0,
          teacher: "陈教授",
          regular_score: 92,
          midterm_score: 89,
          final_score: 94,
          total_score: 92,
          grade_level: "A-",
          gpa_points: 3.7,
          course_type: "必修"
        },
        {
          id: 5,
          course_name: "操作系统",
          course_code: "CS005",
          credits: 3.0,
          teacher: "赵教授",
          regular_score: 78,
          midterm_score: 82,
          final_score: 80,
          total_score: 80,
          grade_level: "B",
          gpa_points: 3.0,
          course_type: "必修"
        },
        {
          id: 6,
          course_name: "软件测试",
          course_code: "CS006",
          credits: 2.0,
          teacher: "刘教授",
          regular_score: 95,
          midterm_score: 93,
          final_score: 96,
          total_score: 95,
          grade_level: "A",
          gpa_points: 4.0,
          course_type: "选修"
        },
        {
          id: 7,
          course_name: "人工智能导论",
          course_code: "CS007",
          credits: 3.0,
          teacher: "孙教授",
          regular_score: 86,
          midterm_score: 84,
          final_score: 87,
          total_score: 86,
          grade_level: "B+",
          gpa_points: 3.3,
          course_type: "选修"
        },
        {
          id: 8,
          course_name: "项目实践",
          course_code: "CS008",
          credits: 4.0,
          teacher: "周教授",
          regular_score: 89,
          midterm_score: 0, // 实践课可能没有期中成绩
          final_score: 91,
          total_score: 90,
          grade_level: "A-",
          gpa_points: 3.7,
          course_type: "实践"
        }
      ]
    },
    
    // 学期选择
    semesterRange: [
      {label: "2024-2025学年 第一学期", value: "2024-1"},
      {label: "2023-2024学年 第二学期", value: "2023-2"},
      {label: "2023-2024学年 第一学期", value: "2023-1"},
      {label: "2022-2023学年 第二学期", value: "2022-2"}
    ],
    semesterIndex: 0,
    
    // 筛选状态
    currentFilter: 'all',
    filteredGrades: [],
    
    // 弹窗
    showModal: false,
    modalData: {},
    
    // 其他状态
    loading: false
  },

  /**
   * 页面加载时
   */
  onLoad() {
    console.log('成绩查询页面加载');
    this.loadGradesData();
    this.applyFilter();
  },

  /**
   * 页面显示时
   */
  onShow() {
    // 刷新数据
    this.refreshData();
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.loadGradesData().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  /**
   * 加载成绩数据
   */
  async loadGradesData() {
    try {
      this.setData({ loading: true });
      
      // 这里应该调用后端API获取成绩数据
      // const res = await wx.request({
      //   url: 'http://localhost:8000/api/v1/simple/grades',
      //   method: 'GET',
      //   data: {
      //     semester: this.data.gradesData.semester_info.current_semester
      //   },
      //   header: {
      //     'Authorization': 'Bearer ' + wx.getStorageSync('token')
      //   }
      // });
      // 
      // if (res.data.success) {
      //   this.setData({
      //     gradesData: res.data.data
      //   });
      //   this.applyFilter();
      // }

      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 500));
      
      console.log('成绩数据加载完成');
    } catch (error) {
      console.error('加载成绩数据失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  /**
   * 刷新数据
   */
  async refreshData() {
    // 静默刷新，不显示loading
    try {
      // 这里可以调用API获取最新数据
      console.log('静默刷新成绩数据');
    } catch (error) {
      console.error('刷新成绩数据失败:', error);
    }
  },

  /**
   * 学期切换
   */
  onSemesterChange(e) {
    const semesterIndex = e.detail.value;
    const semester = this.data.semesterRange[semesterIndex].value;
    
    this.setData({
      semesterIndex,
      'gradesData.semester_info.current_semester': semester
    });
    
    // 重新加载该学期的成绩数据
    this.loadGradesData();
  },

  /**
   * 设置筛选条件
   */
  setFilter(e) {
    const filter = e.currentTarget.dataset.filter;
    this.setData({
      currentFilter: filter
    });
    this.applyFilter();
  },

  /**
   * 应用筛选
   */
  applyFilter() {
    const { currentFilter, gradesData } = this.data;
    let filteredGrades = gradesData.grades;
    
    if (currentFilter !== 'all') {
      filteredGrades = gradesData.grades.filter(grade => 
        grade.course_type === currentFilter
      );
    }
    
    this.setData({
      filteredGrades
    });
  },

  /**
   * 显示成绩详情
   */
  showGradeDetail(e) {
    const grade = e.currentTarget.dataset.grade;
    this.setData({
      showModal: true,
      modalData: grade
    });
  },

  /**
   * 隐藏弹窗
   */
  hideModal() {
    this.setData({
      showModal: false,
      modalData: {}
    });
  },

  /**
   * 阻止冒泡
   */
  stopPropagation() {
    // 阻止点击模态框内容时关闭弹窗
  },

  /**
   * 计算成绩等级对应的CSS类名
   */
  getGradeClass(score) {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  },

  /**
   * 导出成绩单
   */
  exportGrades() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  /**
   * 查看成绩统计
   */
  viewStatistics() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  /**
   * 分享功能
   */
  onShareAppMessage() {
    return {
      title: '我的成绩 - SZTU校园',
      path: '/pages/grades/grades',
      imageUrl: '/assets/icons/Grade.png'
    };
  },

  /**
   * 分享到朋友圈
   */
  onShareTimeline() {
    return {
      title: '我的成绩单 - SZTU校园服务',
      imageUrl: '/assets/icons/Grade.png'
    };
  }
}); 