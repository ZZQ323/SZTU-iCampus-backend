const { BasePage, createPage } = require('../../utils/BasePage')

class SchedulePage extends BasePage {
  getPageName() {
    return '课程表'
  }

  getInitialData() {
    return {
      currentWeek: 1,
      currentSemester: '2024-2025-1',
      loading: false,
      selectedDay: 'monday',
      selectedDayName: '周一',
      selectedDayCourses: [],
      
      dayHeaders: [
        { name: '周一', key: 'monday', date: '12/16', isToday: false },
        { name: '周二', key: 'tuesday', date: '12/17', isToday: false },
        { name: '周三', key: 'wednesday', date: '12/18', isToday: true },
        { name: '周四', key: 'thursday', date: '12/19', isToday: false },
        { name: '周五', key: 'friday', date: '12/20', isToday: false },
        { name: '周六', key: 'saturday', date: '12/21', isToday: false },
        { name: '周日', key: 'sunday', date: '12/22', isToday: false }
      ],
      
      scheduleData: {
        week_info: {
          current_week: 12,
          total_weeks: 18,
          semester: "2024-2025学年第一学期"
        },
        schedule: {
          monday: [], tuesday: [], wednesday: [], thursday: [],
          friday: [], saturday: [], sunday: []
        }
      },
      
      timeSlots: [
        { slot: 1, period: '1-2节', start_time: '08:30', end_time: '10:10' },
        { slot: 2, period: '3-4节', start_time: '10:30', end_time: '12:10' },
        { slot: 3, period: '5-6节', start_time: '14:00', end_time: '15:40' },
        { slot: 4, period: '7-8节', start_time: '16:00', end_time: '17:40' },
        { slot: 5, period: '9-10节', start_time: '19:00', end_time: '20:40' }
      ],
      
      showModal: false,
      modalData: {}
    }
  }

  requiresLogin() {
    return true
  }

  async loadInitialData(options) {
    console.log('📚 课程表页面加载')
    this.setTodayAsDefault()
    await this.initializeSchedule()
  }

  async refreshData(force = false) {
    await this.initializeSchedule()
  }

  async initializeSchedule() {
    try {
      this.setData({ loading: true })
      
      const API = require('../../utils/api')
      const userType = this.data.userInfo?.person_type
      
      if (userType === 'student') {
        const response = await API.getCurrentWeekSchedule()
        
        if (response && response.code === 0) {
          const scheduleData = response.data || {}
          const formattedSchedule = this.formatScheduleData(scheduleData.courses || [])
          
          this.setData({
            'scheduleData.schedule': formattedSchedule,
            'scheduleData.week_info': {
              current_week: scheduleData.current_week || 1,
              total_weeks: scheduleData.total_weeks || 18,
              semester: scheduleData.semester || "2024-2025学年第一学期"
            }
          })
          
          this.updateSelectedDayCourses()
        }
      } else {
        const emptySchedule = {
          monday: [], tuesday: [], wednesday: [], thursday: [],
          friday: [], saturday: [], sunday: []
        }
        this.setData({ 'scheduleData.schedule': emptySchedule })
        this.showToast('您的身份无课表安排', 'none')
      }
      
    } catch (error) {
      console.error('❌ 加载课表失败:', error)
      this.showToast('加载失败', 'error')
    } finally {
      this.setData({ loading: false })
    }
  }

  formatScheduleData(courses) {
    const schedule = {
      monday: [], tuesday: [], wednesday: [], thursday: [],
      friday: [], saturday: [], sunday: []
    }
    
    const weekdayMap = {
      1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday',
      5: 'friday', 6: 'saturday', 7: 'sunday'
    }
    
    courses.forEach(course => {
      const schedule_info = course.schedule || {}
      const weekday = weekdayMap[schedule_info.weekday]
      
      if (weekday) {
        schedule[weekday].push({
          id: course.instance_id,
          course_name: course.course_name,
          teacher: course.teacher_name,
          time: `${schedule_info.start_time}-${schedule_info.end_time}`,
          location: schedule_info.location,
          course_type: course.course_type || "required",
          weeks: schedule_info.weeks || "1-16周"
        })
      }
    })
    
    return schedule
  }

  setTodayAsDefault() {
    const dayHeaders = this.data.dayHeaders
    const todayIndex = dayHeaders.findIndex(day => day.isToday)
    
    if (todayIndex !== -1) {
      this.setData({
        selectedDay: dayHeaders[todayIndex].key,
        selectedDayName: dayHeaders[todayIndex].name
      })
    }
    this.updateSelectedDayCourses()
  }

  onSelectDay(e) {
    const day = e.currentTarget.dataset.day
    const dayHeader = this.data.dayHeaders.find(item => item.key === day)
    
    this.setData({
      selectedDay: day,
      selectedDayName: dayHeader ? dayHeader.name : '未知'
    })
    this.updateSelectedDayCourses()
  }

  updateSelectedDayCourses() {
    const schedule = this.data.scheduleData.schedule
    const selectedDay = this.data.selectedDay
    const selectedDayCourses = schedule[selectedDay] || []
    this.setData({ selectedDayCourses })
  }

  showCourseDetail(e) {
    const course = e.currentTarget.dataset.course
    this.setData({
      modalData: course,
      showModal: true
    })
  }

  hideModal() {
    this.setData({
      showModal: false,
      modalData: {}
    })
  }
}

module.exports = createPage(new SchedulePage()) 