const ResourceClient = require('../ResourceClient')
const DataProcessor = require('../DataProcessor')

/**
 * 课表客户端
 * 处理课表相关的API操作
 * 包括学生课表、教师课表、周次查询等
 */
class ScheduleClient extends ResourceClient {
  constructor() {
    super('http://localhost:8000', 'schedule')
    this.cacheTimeout = 10 * 60 * 1000 // 10分钟缓存
  }

  /**
   * 获取当前周课表
   * @param {boolean} useCache 是否使用缓存
   * @returns {Promise<Object>} 课表数据
   */
  async getCurrentWeekSchedule(useCache = true) {
    const cacheKey = 'current_week_schedule'
    
    if (useCache) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        console.log('[ScheduleClient] 📦 使用缓存的当前周课表')
        return cached
      }
    }

    try {
      const response = await this.request('/schedule/current-week', {
        method: 'GET'
      })
      
      const processedData = this.processScheduleData(response)
      
      // 设置缓存
      this.setCache(cacheKey, processedData, this.cacheTimeout)
      
      return processedData
    } catch (error) {
      console.error('[ScheduleClient] 获取当前周课表失败:', error)
      throw error
    }
  }

  /**
   * 获取指定周次课表
   * @param {number} weekNumber 周次
   * @param {boolean} useCache 是否使用缓存
   * @returns {Promise<Object>} 课表数据
   */
  async getWeekSchedule(weekNumber, useCache = true) {
    const cacheKey = `week_schedule_${weekNumber}`
    
    if (useCache) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        return cached
      }
    }

    try {
      const response = await this.request('/schedule/week', {
        method: 'GET',
        data: { week: weekNumber }
      })
      
      const processedData = this.processScheduleData(response)
      
      this.setCache(cacheKey, processedData, this.cacheTimeout)
      
      return processedData
    } catch (error) {
      console.error('[ScheduleClient] 获取周课表失败:', error)
      throw error
    }
  }

  /**
   * 获取教师课表
   * @param {number} weekNumber 周次，可选
   * @returns {Promise<Object>} 教师课表数据
   */
  async getTeacherSchedule(weekNumber = null) {
    try {
      const params = weekNumber ? { week: weekNumber } : {}
      
      const response = await this.request('/schedule/teacher', {
        method: 'GET',
        data: params
      })
      
      return this.processTeacherScheduleData(response)
    } catch (error) {
      console.error('[ScheduleClient] 获取教师课表失败:', error)
      throw error
    }
  }

  /**
   * 获取学期信息
   * @returns {Promise<Object>} 学期信息
   */
  async getSemesterInfo() {
    const cacheKey = 'semester_info'
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request('/schedule/semester-info', {
        method: 'GET'
      })
      
      const semesterInfo = {
        currentSemester: response.current_semester,
        academicYear: response.academic_year,
        currentWeek: response.current_week,
        totalWeeks: response.total_weeks,
        semesterStartDate: response.start_date,
        semesterEndDate: response.end_date
      }
      
      // 学期信息缓存时间较长
      this.setCache(cacheKey, semesterInfo, 60 * 60 * 1000)
      
      return semesterInfo
    } catch (error) {
      console.error('[ScheduleClient] 获取学期信息失败:', error)
      throw error
    }
  }

  /**
   * 获取今日课程
   * @returns {Promise<Array>} 今日课程列表
   */
  async getTodayCourses() {
    try {
      const currentWeekData = await this.getCurrentWeekSchedule()
      
      // 获取今天是周几
      const today = new Date()
      const weekday = today.getDay() || 7 // 周日为0，转换为7
      
      const weekdayMap = {
        1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday',
        5: 'friday', 6: 'saturday', 7: 'sunday'
      }
      
      const todayKey = weekdayMap[weekday]
      const todayCourses = currentWeekData.schedule[todayKey] || []
      
      // 添加课程状态
      return todayCourses.map(course => ({
        ...course,
        status: this.getCourseStatus(course.time)
      }))
      
    } catch (error) {
      console.error('[ScheduleClient] 获取今日课程失败:', error)
      return []
    }
  }

  /**
   * 获取课程详情
   * @param {string|number} courseId 课程ID
   * @returns {Promise<Object>} 课程详情
   */
  async getCourseDetail(courseId) {
    try {
      const response = await this.request(`/schedule/course/${courseId}`, {
        method: 'GET'
      })
      
      return this.processCourseDetail(response)
    } catch (error) {
      console.error('[ScheduleClient] 获取课程详情失败:', error)
      throw error
    }
  }

  /**
   * 处理课表数据
   * @param {Object} data 原始课表数据
   * @returns {Object} 处理后的课表数据
   */
  processScheduleData(data) {
    if (!data || typeof data !== 'object') {
      return this.getEmptySchedule()
    }

    const schedule = {
      monday: [], tuesday: [], wednesday: [], thursday: [],
      friday: [], saturday: [], sunday: []
    }
    
    const weekdayMap = {
      1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday',
      5: 'friday', 6: 'saturday', 7: 'sunday'
    }
    
    const courses = data.courses || []
    
    courses.forEach(course => {
      const scheduleInfo = course.schedule || {}
      const weekday = weekdayMap[scheduleInfo.weekday]
      
      if (weekday) {
        schedule[weekday].push({
          id: course.instance_id || course.course_id,
          courseName: course.course_name,
          teacher: course.teacher_name,
          time: `${scheduleInfo.start_time}-${scheduleInfo.end_time}`,
          timeSlot: course.time_slot || "1-2",
          location: scheduleInfo.location,
          courseType: course.course_type || "required",
          weeks: scheduleInfo.weeks || "1-16周",
          status: "upcoming",
          note: course.note || "",
          courseCode: course.course_code,
          credits: course.credits
        })
      }
    })
    
    return {
      weekInfo: {
        currentWeek: data.current_week || 1,
        totalWeeks: data.total_weeks || 18,
        semester: data.semester || "当前学期",
        semesterDisplayName: DataProcessor.formatSemester(data.semester || "2024-2025-1")
      },
      schedule: schedule,
      summary: this.calculateWeekSummary(schedule)
    }
  }

  /**
   * 处理教师课表数据
   * @param {Object} data 原始教师课表数据
   * @returns {Object} 处理后的教师课表数据
   */
  processTeacherScheduleData(data) {
    if (!data || typeof data !== 'object') {
      return this.getEmptySchedule()
    }

    const schedule = {
      monday: [], tuesday: [], wednesday: [], thursday: [],
      friday: [], saturday: [], sunday: []
    }
    
    const weekdayMap = {
      1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday',
      5: 'friday', 6: 'saturday', 7: 'sunday'
    }
    
    const teachingSchedule = data.teaching_schedule || []
    
    teachingSchedule.forEach(course => {
      const weekday = weekdayMap[course.weekday]
      if (weekday) {
        schedule[weekday].push({
          id: course.course_id,
          courseName: course.course_name,
          className: course.class_name,
          time: `${course.start_time}-${course.end_time}`,
          timeSlot: course.time_slot || "1-2",
          location: course.location,
          courseType: course.course_type || "required",
          weeks: course.weeks || "1-16周",
          status: "upcoming",
          studentCount: course.student_count || 0,
          courseCode: course.course_code
        })
      }
    })
    
    return {
      weekInfo: {
        currentWeek: data.current_week || 1,
        totalWeeks: data.total_weeks || 18,
        semester: data.semester || "当前学期",
        semesterDisplayName: DataProcessor.formatSemester(data.semester || "2024-2025-1")
      },
      schedule: schedule,
      summary: this.calculateWeekSummary(schedule)
    }
  }

  /**
   * 处理课程详情
   * @param {Object} data 原始课程详情
   * @returns {Object} 处理后的课程详情
   */
  processCourseDetail(data) {
    return {
      id: data.course_id,
      courseName: data.course_name,
      courseCode: data.course_code,
      credits: data.credits,
      teacher: data.teacher_name,
      teacherInfo: data.teacher_info || {},
      time: `${data.start_time}-${data.end_time}`,
      location: data.location,
      courseType: data.course_type,
      weeks: data.weeks,
      description: data.description || '',
      syllabus: data.syllabus || '',
      assessment: data.assessment || '',
      textbooks: data.textbooks || [],
      prerequisites: data.prerequisites || [],
      classmates: data.classmates || []
    }
  }

  /**
   * 计算周课程统计
   * @param {Object} schedule 课表数据
   * @returns {Object} 统计信息
   */
  calculateWeekSummary(schedule) {
    let totalCourses = 0
    let requiredCourses = 0
    let electiveCourses = 0
    let practicalCourses = 0

    Object.values(schedule).forEach(dayCourses => {
      dayCourses.forEach(course => {
        totalCourses++
        switch (course.courseType) {
          case 'required':
            requiredCourses++
            break
          case 'elective':
            electiveCourses++
            break
          case 'practical':
            practicalCourses++
            break
        }
      })
    })

    return {
      totalCourses,
      requiredCourses,
      electiveCourses,
      practicalCourses
    }
  }

  /**
   * 判断课程状态
   * @param {string} timeRange 时间范围，如 "08:30-10:10"
   * @returns {string} 课程状态
   */
  getCourseStatus(timeRange) {
    if (!timeRange || !timeRange.includes('-')) {
      return 'upcoming'
    }

    const [startTime, endTime] = timeRange.split('-')
    const now = new Date()
    const currentTime = now.getHours() * 60 + now.getMinutes()
    
    const [startHour, startMin] = startTime.split(':').map(Number)
    const [endHour, endMin] = endTime.split(':').map(Number)
    
    const courseStart = startHour * 60 + startMin
    const courseEnd = endHour * 60 + endMin
    
    if (currentTime < courseStart) {
      return 'upcoming'
    } else if (currentTime >= courseStart && currentTime <= courseEnd) {
      return 'current'
    } else {
      return 'completed'
    }
  }

  /**
   * 获取空课表
   * @returns {Object} 空课表数据
   */
  getEmptySchedule() {
    return {
      weekInfo: {
        currentWeek: 1,
        totalWeeks: 18,
        semester: "当前学期",
        semesterDisplayName: "当前学期"
      },
      schedule: {
        monday: [], tuesday: [], wednesday: [], thursday: [],
        friday: [], saturday: [], sunday: []
      },
      summary: {
        totalCourses: 0,
        requiredCourses: 0,
        electiveCourses: 0,
        practicalCourses: 0
      }
    }
  }

  /**
   * 错误处理
   * @param {Error} error 错误对象
   * @param {string} url 请求URL
   */
  handleError(error, url) {
    console.error(`[ScheduleClient] ❌ 请求失败:`, url, error.message)
    
    if (error.message.includes('401')) {
      throw new Error('登录已过期，请重新登录后查看课表')
    } else if (error.message.includes('403')) {
      throw new Error('暂无权限查看课表信息')
    } else if (error.message.includes('网络')) {
      throw new Error('网络连接失败，请检查网络设置')
    } else {
      throw error
    }
  }
}

module.exports = ScheduleClient 