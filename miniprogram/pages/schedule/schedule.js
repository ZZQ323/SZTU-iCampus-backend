const app = getApp()
const API = require('../../utils/api.js')

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

  async initializeSchedule() {
    if (!this.data.userInfo) {
      return;
    }

    this.setData({ loading: true });

    try {
    const userType = this.data.userInfo.person_type;

    if (userType === 'student') {
        // 学生获取课表数据
        const response = await API.getCurrentWeekSchedule();
        
        if (response.code === 0) {
          const scheduleData = response.data || {};
          
          // 转换API数据格式为前端需要的格式
          const formattedSchedule = this.formatScheduleData(scheduleData.courses || []);
          
          this.setData({
            'scheduleData.schedule': formattedSchedule,
            'scheduleData.week_info': {
              current_week: scheduleData.current_week || 1,
              total_weeks: scheduleData.total_weeks || 18,
              semester: scheduleData.semester || "2024-2025学年第一学期"
            }
          });
        } else {
          throw new Error(response.message || '获取学生课表失败');
        }
    } else if (userType === 'teacher' || userType === 'assistant_teacher') {
        // 教师获取教学安排
        const response = await API.getTeacherSchedule();
        
        if (response.code === 0) {
          const scheduleData = response.data || {};
          
          // 转换教师课表数据格式
          const formattedSchedule = this.formatTeacherScheduleData(scheduleData.teaching_schedule || []);
          
          this.setData({
            'scheduleData.schedule': formattedSchedule,
            'scheduleData.week_info': {
              current_week: scheduleData.current_week || 1,
              total_weeks: scheduleData.total_weeks || 18,
              semester: scheduleData.semester || "2024-2025学年第一学期"
            }
          });
        } else {
          throw new Error(response.message || '获取教师课表失败');
        }
    } else {
      // 管理员等其他角色没有课表
        const emptySchedule = {
          monday: [], tuesday: [], wednesday: [], thursday: [],
          friday: [], saturday: [], sunday: []
      };
      
        this.setData({
          'scheduleData.schedule': emptySchedule
        });
        
      wx.showToast({
        title: '您的身份无课表安排',
        icon: 'none',
        duration: 2000
      });
    }
      
      // 计算课程统计
      this.calculateWeekSummary();
      
    } catch (error) {
      console.error('[课表页面] ❌ 加载课表失败:', error);
      
      // 出错时使用空课表
      const emptySchedule = {
        monday: [], tuesday: [], wednesday: [], thursday: [],
        friday: [], saturday: [], sunday: []
      };

    this.setData({
        'scheduleData.schedule': emptySchedule
    });

      wx.showToast({
        title: '加载课表失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  /**
   * 格式化学生课表数据
   */
  formatScheduleData(courses) {
    const schedule = {
      monday: [], tuesday: [], wednesday: [], thursday: [],
      friday: [], saturday: [], sunday: []
    };
    
    const weekdayMap = {
      1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday',
      5: 'friday', 6: 'saturday', 7: 'sunday'
    };
    
    courses.forEach(course => {
      const schedule_info = course.schedule || {};
      const weekday = weekdayMap[schedule_info.weekday];
      if (weekday) {
        schedule[weekday].push({
          id: course.instance_id,
          course_name: course.course_name,
          teacher: course.teacher_name,
          time: `${schedule_info.start_time}-${schedule_info.end_time}`,
          time_slot: course.time_slot || "1-2",
          location: schedule_info.location,
          course_type: course.course_type || "required",
          weeks: schedule_info.weeks || "1-16周",
          status: "upcoming",
          note: course.note || ""
        });
      }
    });
    
    return schedule;
  },

  /**
   * 格式化教师课表数据
   */
  formatTeacherScheduleData(teachingSchedule) {
    const schedule = {
      monday: [], tuesday: [], wednesday: [], thursday: [],
      friday: [], saturday: [], sunday: []
    };
    
    const weekdayMap = {
      1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday',
      5: 'friday', 6: 'saturday', 7: 'sunday'
    };
    
    teachingSchedule.forEach(course => {
      const weekday = weekdayMap[course.weekday];
      if (weekday) {
        schedule[weekday].push({
          id: course.course_id,
          course_name: course.course_name,
          class_name: course.class_name,
          time: `${course.start_time}-${course.end_time}`,
          time_slot: course.time_slot || "1-2",
          location: course.location,
          course_type: course.course_type || "required",
          weeks: course.weeks || "1-16周",
          status: "upcoming",
          student_count: course.student_count || 0
        });
      }
    });
    
    return schedule;
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

  async onWeekChange(e) {
    const weekIndex = e.detail.value;
    const weekData = this.data.weekRange[weekIndex];
    
    this.setData({
      weekIndex: weekIndex,
      'scheduleData.week_info.current_week': weekData.value
    });
    
    // 调用API获取对应周次的课表
    await this.loadWeekSchedule(weekData.value);
  },

  /**
   * 加载指定周次的课表
   */
  async loadWeekSchedule(weekNumber) {
    if (!this.data.userInfo) return;
    
    try {
      this.setData({ loading: true });
      
      const userType = this.data.userInfo.person_type;
      let response;
      
      if (userType === 'student') {
        response = await API.getWeekSchedule(weekNumber);
      } else if (userType === 'teacher' || userType === 'assistant_teacher') {
        response = await API.getTeacherWeekSchedule(weekNumber);
      } else {
        return;
      }
      
      if (response.code === 0) {
        const scheduleData = response.data || {};
        let formattedSchedule;
        
        if (userType === 'student') {
          formattedSchedule = this.formatScheduleData(scheduleData.courses || []);
        } else {
          formattedSchedule = this.formatTeacherScheduleData(scheduleData.teaching_schedule || []);
        }
        
        this.setData({
          'scheduleData.schedule': formattedSchedule
        });
        
        this.calculateWeekSummary();
        this.updateSelectedDayCourses();
      }
    } catch (error) {
      console.error('[课表页面] ❌ 加载周课表失败:', error);
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
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
    this.initializeSchedule().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadScheduleData() {
    if (!this.data.isLoggedIn) {
      return;
    }

    try {
      this.setData({ loading: true });
      await this.initializeSchedule();
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