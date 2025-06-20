const app = getApp()

Page({
  data: {
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
    todayCourses: [
      {
        id: 1,
        course_name: "数据结构与算法",
        teacher: "李教授",
        time: "08:30-10:10",
        location: "C2-301",
        status: "upcoming"
      },
      {
        id: 2,
        course_name: "软件工程",
        teacher: "王教授",
        time: "10:30-12:10",
        location: "C2-305",
        status: "current"
      },
      {
        id: 3,
        course_name: "数据库原理",
        teacher: "张教授",
        time: "14:30-16:10",
        location: "C2-302",
        status: "upcoming"
      }
    ],
    
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
      totalCourses: 18,
      requiredCourses: 12,
      electiveCourses: 4,
      practicalCourses: 2
    }
  },

  onLoad() {
    console.log('课表页面加载');
    this.initializeSchedule();
    this.setTodayAsDefault();
  },

  onShow() {
    this.updateSelectedDayCourses();
  },

  initializeSchedule() {
    // 模拟课表数据
    const mockSchedule = {
      monday: [
        {
          id: 1,
          course_name: "数据结构与算法",
          teacher: "李教授",
          time: "08:30-10:10",
          time_slot: "1-2",
          location: "C2-301",
          course_type: "required",
          weeks: "1-16周",
          status: "upcoming",
          note: "请携带笔记本电脑"
        },
        {
          id: 2,
          course_name: "软件工程",
          teacher: "王教授", 
          time: "10:30-12:10",
          time_slot: "3-4",
          location: "C2-305",
          course_type: "required",
          weeks: "1-16周",
          status: "upcoming"
        },
        {
          id: 3,
          course_name: "数据库原理",
          teacher: "张教授",
          time: "14:30-16:10", 
          time_slot: "7-8",
          location: "C2-302",
          course_type: "required",
          weeks: "1-16周",
          status: "upcoming"
        }
      ],
      tuesday: [
        {
          id: 4,
          course_name: "计算机网络",
          teacher: "陈教授",
          time: "08:30-10:10",
          time_slot: "1-2", 
          location: "B3-201",
          course_type: "required",
          weeks: "1-16周",
          status: "upcoming"
        },
        {
          id: 5,
          course_name: "人工智能导论",
          teacher: "刘教授",
          time: "14:30-16:10",
          time_slot: "7-8",
          location: "A1-105",
          course_type: "elective",
          weeks: "1-16周", 
          status: "upcoming"
        }
      ],
      wednesday: [
        {
          id: 6,
          course_name: "操作系统",
          teacher: "赵教授",
          time: "08:30-10:10",
          time_slot: "1-2",
          location: "C2-303",
          course_type: "required",
          weeks: "1-16周",
          status: "current",
          note: "今日有随堂测验"
        },
        {
          id: 7,
          course_name: "编译原理",
          teacher: "孙教授",
          time: "10:30-12:10",
          time_slot: "3-4",
          location: "C2-306",
          course_type: "required",
          weeks: "1-16周",
          status: "finished"
        }
      ],
      thursday: [
        {
          id: 8,
          course_name: "算法设计与分析",
          teacher: "钱教授",
          time: "08:30-10:10",
          time_slot: "1-2",
          location: "C2-304",
          course_type: "required",
          weeks: "1-16周",
          status: "upcoming"
        },
        {
          id: 9,
          course_name: "移动应用开发",
          teacher: "周教授",
          time: "14:30-16:10",
          time_slot: "7-8",
          location: "D1-301",
          course_type: "elective",
          weeks: "1-16周",
          status: "upcoming"
        }
      ],
      friday: [
        {
          id: 10,
          course_name: "软件测试",
          teacher: "吴教授",
          time: "08:30-10:10",
          time_slot: "1-2",
          location: "C2-307",
          course_type: "required",
          weeks: "1-16周",
          status: "upcoming"
        },
        {
          id: 11,
          course_name: "项目实训",
          teacher: "郑教授",
          time: "14:30-17:00",
          time_slot: "7-9",
          location: "实训室A",
          course_type: "practical",
          weeks: "1-16周",
          status: "upcoming",
          note: "分组进行项目开发"
        }
      ],
      saturday: [],
      sunday: []
    };

    this.setData({
      'scheduleData.schedule': mockSchedule
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
    this.loadScheduleData().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadScheduleData() {
    try {
      this.setData({ loading: true });
      
      // 这里应该调用后端API获取课表数据
      // const res = await wx.request({
      //   url: 'http://localhost:8000/api/v1/schedule',
      //   method: 'GET',
      //   data: {
      //     week: this.data.scheduleData.week_info.current_week
      //   },
      //   header: {
      //     'Authorization': 'Bearer ' + wx.getStorageSync('token')
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