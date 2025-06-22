const app = getApp()

Page({
  data: {
    // 用户状态
    userInfo: null,
    isLoggedIn: false,
    
    // 当前状态
    currentWeek: 1,
    currentSemester: '2024-2025-1',
    semesterStartDate: '2024-09-02',
    loading: false,
    selectedDay: 'monday',
    selectedDayName: '周一',
    selectedDayCourses: [],
    
    // 星期数据
    weekDays: [
      { name: '周一', date: '11-25' },
      { name: '周二', date: '11-26' },
      { name: '周三', date: '11-27' },
      { name: '周四', date: '11-28' },
      { name: '周五', date: '11-29' },
      { name: '周六', date: '11-30' },
      { name: '周日', date: '12-01' }
    ],
    
    // 时间段信息
    timeSlots: [
      { slot: 1, period: '1-2节', start_time: '08:30', end_time: '10:10' },
      { slot: 2, period: '3-4节', start_time: '10:30', end_time: '12:10' },
      { slot: 3, period: '5-6节', start_time: '14:00', end_time: '15:40' },
      { slot: 4, period: '7-8节', start_time: '16:00', end_time: '17:40' },
      { slot: 5, period: '9-10节', start_time: '19:00', end_time: '20:40' }
    ],
    
    // 课表数据 [周一到周日][第几节课]
    scheduleData: {
      week_info: {
        current_week: 12,
        total_weeks: 18,
        semester: "2024-2025学年第一学期"
      },
      schedule: {}
    },
    
    // 星期标题
    dayHeaders: [
      { name: '周一', key: 'monday', date: '12/16', isToday: false },
      { name: '周二', key: 'tuesday', date: '12/17', isToday: false },
      { name: '周三', key: 'wednesday', date: '12/18', isToday: true },
      { name: '周四', key: 'thursday', date: '12/19', isToday: false },
      { name: '周五', key: 'friday', date: '12/20', isToday: false },
      { name: '周六', key: 'saturday', date: '12/21', isToday: false },
      { name: '周日', key: 'sunday', date: '12/22', isToday: false }
    ],
    
    // 今日课程
    todayCourses: [],
    
    // 周次选择器
    weekRange: [
      { label: "第1周", value: 1 },
      { label: "第2周", value: 2 },
      { label: "第3周", value: 3 },
      { label: "第4周", value: 4 },
      { label: "第5周", value: 5 },
      { label: "第6周", value: 6 },
      { label: "第7周", value: 7 },
      { label: "第8周", value: 8 },
      { label: "第9周", value: 9 },
      { label: "第10周", value: 10 },
      { label: "第11周", value: 11 },
      { label: "第12周", value: 12 },
      { label: "第13周", value: 13 },
      { label: "第14周", value: 14 },
      { label: "第15周", value: 15 },
      { label: "第16周", value: 16 },
      { label: "第17周", value: 17 },
      { label: "第18周", value: 18 }
    ],
    weekIndex: 11,
    
    // 弹窗
    showModal: false,
    modalData: {},
    
    // 其他状态
    isEmpty: false,
    
    // 周课程统计
    weekSummary: {
      totalCourses: 0,
      requiredCourses: 0,
      electiveCourses: 0,
      practicalCourses: 0
    }
  },

  onLoad() {
    console.log('课表页面加载');
    this.checkLoginStatus();
  },

  onShow() {
    this.checkLoginStatus();
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo
      });
      console.log('用户已登录:', userInfo);
      this.initializeSchedule();
      this.setTodayAsDefault();
    } else {
      this.setData({
        isLoggedIn: false,
        userInfo: null
      });
      this.showLoginPrompt();
    }
  },

  /**
   * 显示登录提示
   */
  showLoginPrompt() {
    wx.showModal({
      title: '需要登录',
      content: '查看课表需要先登录，是否前往登录？',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: '/pages/login/login'
          });
        } else {
          wx.switchTab({
            url: '/pages/index/index'
          });
        }
      }
    });
  },

  initializeSchedule() {
    if (!this.data.userInfo) {
      return;
    }

    const userType = this.data.userInfo.person_type;
    let mockSchedule = {};

    if (userType === 'student') {
      // 学生课表
      mockSchedule = {
        monday: [
          {
            id: 1,
            course_name: "高等数学A",
            teacher: "张教授",
            time: "08:30-10:10",
            time_slot: "1-2",
            location: "C2-301",
            course_type: "required",
            weeks: "1-16周",
            status: "upcoming",
            note: "请携带教材"
          },
          {
            id: 2,
            course_name: "程序设计基础",
            teacher: "李教授",
            time: "10:30-12:10",
            time_slot: "3-4",
            location: "C2-305",
            course_type: "required",
            weeks: "1-16周",
            status: "upcoming"
          }
        ],
        tuesday: [
          {
            id: 3,
            course_name: "英语",
            teacher: "王教授",
            time: "08:30-10:10",
            time_slot: "1-2",
            location: "B3-201",
            course_type: "required",
            weeks: "1-16周",
            status: "upcoming"
          }
        ],
        wednesday: [
          {
            id: 4,
            course_name: "体育",
            teacher: "赵教练",
            time: "14:00-15:40",
            time_slot: "5-6",
            location: "体育馆",
            course_type: "required",
            weeks: "1-16周",
            status: "upcoming"
          }
        ],
        thursday: [],
        friday: [],
        saturday: [],
        sunday: []
      };
    } else if (userType === 'teacher' || userType === 'assistant_teacher') {
      // 教师课表
      mockSchedule = {
        monday: [
          {
            id: 1,
            course_name: "软件工程",
            class_name: "软工2024-1班",
            time: "08:30-10:10",
            time_slot: "1-2",
            location: "C2-301",
            course_type: "required",
            weeks: "1-16周",
            status: "upcoming",
            student_count: 58
          },
          {
            id: 2,
            course_name: "软件工程",
            class_name: "软工2024-2班",
            time: "10:30-12:10",
            time_slot: "3-4",
            location: "C2-305",
            course_type: "required",
            weeks: "1-16周",
            status: "upcoming",
            student_count: 56
          }
        ],
        tuesday: [],
        wednesday: [
          {
            id: 3,
            course_name: "数据库原理",
            class_name: "计科2024-1班",
            time: "14:00-15:40",
            time_slot: "5-6",
            location: "C3-201",
            course_type: "required",
            weeks: "1-16周",
            status: "upcoming",
            student_count: 62
          }
        ],
        thursday: [],
        friday: [],
        saturday: [],
        sunday: []
      };
    } else {
      // 管理员等其他角色没有课表
      mockSchedule = {
        monday: [],
        tuesday: [],
        wednesday: [],
        thursday: [],
        friday: [],
        saturday: [],
        sunday: []
      };
      
      // 显示提示信息
      wx.showToast({
        title: '您的身份无课表安排',
        icon: 'none',
        duration: 2000
      });
    }

    this.setData({
      'scheduleData.schedule': mockSchedule
    });

    // 计算课程统计
    this.calculateWeekSummary();
  },

  /**
   * 计算周课程统计
   */
  calculateWeekSummary() {
    const schedule = this.data.scheduleData.schedule;
    let totalCourses = 0;
    let requiredCourses = 0;
    let electiveCourses = 0;
    let practicalCourses = 0;

    Object.values(schedule).forEach(dayCourses => {
      dayCourses.forEach(course => {
        totalCourses++;
        switch (course.course_type) {
          case 'required':
            requiredCourses++;
            break;
          case 'elective':
            electiveCourses++;
            break;
          case 'practical':
            practicalCourses++;
            break;
        }
      });
    });

    this.setData({
      weekSummary: {
        totalCourses,
        requiredCourses,
        electiveCourses,
        practicalCourses
      }
    });
  },

  setTodayAsDefault() {
    const dayHeaders = this.data.dayHeaders;
    const todayIndex = dayHeaders.findIndex(day => day.isToday);
    
    if (todayIndex !== -1) {
      this.setData({
        selectedDay: dayHeaders[todayIndex].key,
        selectedDayName: dayHeaders[todayIndex].name
      });
    }
    
    this.updateSelectedDayCourses();
  },

  onSelectDay(e) {
    const day = e.currentTarget.dataset.day;
    const dayHeader = this.data.dayHeaders.find(item => item.key === day);
    
    this.setData({
      selectedDay: day,
      selectedDayName: dayHeader ? dayHeader.name : '未知'
    });
    
    this.updateSelectedDayCourses();
  },

  updateSelectedDayCourses() {
    const schedule = this.data.scheduleData.schedule;
    const selectedDayCourses = schedule[this.data.selectedDay] || [];
    
    this.setData({
      selectedDayCourses: selectedDayCourses
    });
  },

  onWeekChange(e) {
    const weekIndex = e.detail.value;
    const weekData = this.data.weekRange[weekIndex];
    
    this.setData({
      weekIndex: weekIndex,
      'scheduleData.week_info.current_week': weekData.value
    });
    
    // 这里可以调用API获取对应周次的课表
    console.log(`切换到第${weekData.value}周`);
  },

  showCourseDetail(e) {
    const course = e.currentTarget.dataset.course;
    this.setData({
      modalData: course,
      showModal: true
    });
  },

  hideModal() {
    this.setData({
      showModal: false,
      modalData: {}
    });
  },

  onPullDownRefresh() {
    this.checkLoginStatus();
    this.loadScheduleData().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadScheduleData() {
    if (!this.data.isLoggedIn) {
      return;
    }

    try {
      this.setData({ loading: true });
      
      // TODO: 调用后端API获取课表数据
      // const token = wx.getStorageSync('token');
      // const res = await wx.request({
      //   url: 'http://localhost:8000/api/v1/simple/schedule',
      //   method: 'GET',
      //   data: {
      //     week: this.data.scheduleData.week_info.current_week
      //   },
      //   header: {
      //     'Authorization': 'Bearer ' + token
      //   }
      // });
      
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 800));
      
      console.log('课表数据加载完成');
    } catch (error) {
      console.error('加载课表数据失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  onShareAppMessage() {
    return {
      title: '我的课表 - SZTU校园',
      path: '/pages/schedule/schedule',
      imageUrl: '/assets/icons/schedule.png'
    };
  },

  onShareTimeline() {
    return {
      title: '我的课表 - SZTU校园服务',
      imageUrl: '/assets/icons/schedule.png'
    };
  }
}) 