const app = getApp()

Page({
  data: {
    // 当前状态
    currentWeek: 1,
    currentSemester: '2024-2025-1',
    semesterStartDate: '2024-09-02',
    loading: false,
    
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
    scheduleData: [],
    
    // 今日课程
    todayCourses: [],
    todayIndex: 0,
    
    // 用户信息
    userInfo: {}
  },

  onLoad() {
    this.getUserInfo()
    this.initializeData()
    
    // 获取当前周次后再获取课表数据
    this.getCurrentWeek().then(() => {
      this.fetchScheduleData()
    })
  },

  onShow() {
    this.updateTodayInfo()
    // 只在有数据时更新今日课程，避免重复请求
    if (this.data.scheduleData.length > 0) {
      this.getTodayCourses(this.data.todayIndex)
    }
  },

  // 获取用户信息
  getUserInfo() {
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({ userInfo })
    }
  },

  // 获取当前周次
  getCurrentWeek() {
    return new Promise((resolve) => {
      const token = wx.getStorageSync('token')
      if (!token) {
        this.setData({ currentWeek: 1 })
        resolve()
        return
      }
      
      wx.request({
        url: `${app.globalData.baseURL}/api/v1/schedule/current-week`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: {
          semester: this.data.currentSemester,
          semester_start: this.data.semesterStartDate
        },
        success: (res) => {
          if (res.statusCode === 200 && res.data.current_week) {
            this.setData({
              currentWeek: res.data.current_week
            })
          }
          resolve()
        },
        fail: (error) => {
          console.error('获取当前周次失败:', error)
          this.setData({ currentWeek: 1 })
          resolve()
        }
      })
    })
  },

  // 初始化数据
  initializeData() {
    // 初始化空课表
    const scheduleData = []
    for (let day = 0; day < 7; day++) {
      scheduleData[day] = []
      for (let time = 0; time < 5; time++) {
        scheduleData[day][time] = null
      }
    }
    
    this.setData({ scheduleData })
    this.updateTodayInfo()
  },

  // 更新今日信息
  updateTodayInfo() {
    const today = new Date().getDay()
    const todayIndex = today === 0 ? 6 : today - 1 // 转换为0-6，周一为0
    
    // 更新星期显示
    const weekDays = this.data.weekDays.map((day, index) => {
      const date = new Date()
      date.setDate(date.getDate() + index - todayIndex)
      return {
        ...day,
        date: `${date.getMonth() + 1}-${date.getDate().toString().padStart(2, '0')}`
      }
    })
    
    this.setData({
      weekDays,
      todayIndex
    })
    
    // 获取今日课程
    this.getTodayCourses(todayIndex)
  },

  // 获取今日课程
  getTodayCourses(dayIndex) {
    const { scheduleData, timeSlots } = this.data
    const todayCourses = []
    const now = new Date()
    const currentTime = now.getHours() * 60 + now.getMinutes()
    
    if (scheduleData[dayIndex]) {
      scheduleData[dayIndex].forEach((course, timeIndex) => {
        if (course) {
          const timeSlot = timeSlots[timeIndex]
          const [startTime, endTime] = [timeSlot.start_time, timeSlot.end_time]
          const [startHour, startMin] = startTime.split(':').map(Number)
          const [endHour, endMin] = endTime.split(':').map(Number)
          
          const courseStartTime = startHour * 60 + startMin
          const courseEndTime = endHour * 60 + endMin
          
          let status = 'upcoming'
          let statusText = '即将开始'
          
          if (currentTime >= courseStartTime && currentTime <= courseEndTime) {
            status = 'ongoing'
            statusText = '进行中'
          } else if (currentTime > courseEndTime) {
            status = 'finished'
            statusText = '已结束'
          }
          
          todayCourses.push({
            ...course,
            timeRange: `${startTime}-${endTime}`,
            status,
            statusText
          })
        }
      })
    }
    
    this.setData({ todayCourses })
  },

  // 获取课表数据
  fetchScheduleData() {
    this.setData({ loading: true })
    
    const token = wx.getStorageSync('token')
    if (!token) {
      this.setData({ loading: false })
      this.generateMockSchedule() // 使用模拟数据
      return
    }
    
    wx.request({
      url: `${app.globalData.baseURL}/api/v1/schedule/grid/${this.data.currentWeek}`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        semester: this.data.currentSemester
      },
      success: (res) => {
        console.log('课表API响应:', res)
        
        if (res.statusCode === 200) {
          const { schedule_data, time_slots } = res.data
          
          this.setData({
            scheduleData: schedule_data || [],
            timeSlots: time_slots || this.data.timeSlots
          })
          
          // 更新今日课程
          this.getTodayCourses(this.data.todayIndex)
        } else {
          console.error('API返回错误状态:', res.statusCode)
          this.generateMockSchedule()
        }
        
        this.setData({ loading: false })
      },
      fail: (error) => {
        console.error('获取课表失败:', error)
        wx.showToast({
          title: '获取课表失败，使用模拟数据',
          icon: 'none'
        })
        
        // 使用模拟数据
        this.generateMockSchedule()
        this.setData({ loading: false })
      }
    })
  },

  // 生成模拟课表数据（备用）
  generateMockSchedule() {
    const schedule = []
    
    // 初始化空课表
    for (let day = 0; day < 7; day++) {
      schedule[day] = []
      for (let time = 0; time < 5; time++) {
        schedule[day][time] = null
      }
    }
    
    // 添加一些示例课程
    const courses = [
      { course_name: '高等数学', teacher: '张教授', classroom: 'A101', course_type: '必修' },
      { course_name: '数据结构', teacher: '李老师', classroom: 'B205', course_type: '必修' },
      { course_name: '计算机网络', teacher: '王老师', classroom: 'C303', course_type: '必修' },
      { course_name: '软件工程', teacher: '赵老师', classroom: 'D401', course_type: '选修' },
      { course_name: '数据库实验', teacher: '钱老师', classroom: '实验室1', course_type: '实验' },
      { course_name: '毕业设计', teacher: '孙老师', classroom: 'E502', course_type: '实践' }
    ]
    
    // 随机分配课程到课表中
    const assignments = [
      [0, 0, 0], [0, 1, 1], [1, 0, 2], [1, 2, 3], 
      [2, 1, 4], [2, 3, 1], [3, 0, 5], [3, 2, 0],
      [4, 1, 2], [4, 3, 3]
    ]
    
    assignments.forEach(([day, time, courseIndex]) => {
      if (courses[courseIndex]) {
        schedule[day][time] = {
          id: `${day}-${time}`,
          ...courses[courseIndex]
        }
      }
    })
    
    this.setData({ scheduleData: schedule })
  },

  // 切换周次
  changeWeek() {
    // 生成周次选项
    const weekOptions = []
    for (let i = 1; i <= 20; i++) {
      weekOptions.push(`第${i}周`)
    }
    
    wx.showActionSheet({
      itemList: weekOptions,
      success: (res) => {
        const selectedWeek = res.tapIndex + 1 // tapIndex从0开始，所以+1
        
        this.setData({
          currentWeek: selectedWeek
        })
        
        // 重新获取该周课表数据
        this.fetchScheduleData()
        
        wx.showToast({
          title: `已切换到第${selectedWeek}周`,
          icon: 'success'
        })
      },
      fail: (res) => {
        console.log('用户取消选择')
      }
    })
  },

  // 查看课程详情
  viewCourseDetail(e) {
    const course = e.currentTarget.dataset.course
    
    if (!course) return
    
    // 存储到全局数据
    app.globalData.currentCourse = course
    
    wx.navigateTo({
      url: '/pages/course-detail/course-detail'
    })
  },

  // 添加课程
  addCourse(e) {
    const { day, time } = e.currentTarget.dataset
    
    // 存储位置信息
    app.globalData.addCoursePosition = {
      weekDay: parseInt(day) + 1, // 转换为1-7
      timeSlot: parseInt(time) + 1, // 转换为1-5
      currentWeek: this.data.currentWeek,
      semester: this.data.currentSemester
    }
    
    wx.navigateTo({
      url: '/pages/course-editor/course-editor'
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.fetchScheduleData()
    
    // 延迟停止下拉刷新
    setTimeout(() => {
      wx.stopPullDownRefresh()
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    }, 1000)
  }
}) 