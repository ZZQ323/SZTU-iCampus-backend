Page({
  data: {
    course: {
      course_name: '',
      teacher: '',
      classroom: '',
      week_day: 1,
      start_time: '08:30',
      end_time: '10:10',
      weeks: '1-16',
      course_type: '必修',
      credits: '2'
    },
    weekDays: [
      { label: '周一', value: 1 },
      { label: '周二', value: 2 },
      { label: '周三', value: 3 },
      { label: '周四', value: 4 },
      { label: '周五', value: 5 },
      { label: '周六', value: 6 },
      { label: '周日', value: 7 }
    ],
    timeSlots: [
      { label: '第1-2节', value: '08:30-10:10' },
      { label: '第3-4节', value: '10:30-12:10' },
      { label: '第5-6节', value: '14:00-15:40' },
      { label: '第7-8节', value: '16:00-17:40' },
      { label: '第9-10节', value: '19:00-20:40' }
    ],
    courseTypes: ['必修', '选修', '实践', '实验'],
    isEdit: false,
    courseId: null
  },

  onLoad(options) {
    if (options.courseId) {
      this.setData({
        isEdit: true,
        courseId: options.courseId
      })
      this.loadCourseData(options.courseId)
    }
  },

  loadCourseData(courseId) {
    // 这里应该从本地存储或服务器加载课程数据
    // 暂时使用模拟数据
    const course = {
      course_name: '高等数学',
      teacher: '张教授',
      classroom: 'A101',
      week_day: 1,
      start_time: '08:30',
      end_time: '10:10',
      weeks: '1-16',
      course_type: '必修',
      credits: '4'
    }
    
    this.setData({ course })
  },

  // 表单输入处理
  onCourseNameInput(e) {
    this.setData({
      'course.course_name': e.detail.value
    })
  },

  onTeacherInput(e) {
    this.setData({
      'course.teacher': e.detail.value
    })
  },

  onClassroomInput(e) {
    this.setData({
      'course.classroom': e.detail.value
    })
  },

  onWeeksInput(e) {
    this.setData({
      'course.weeks': e.detail.value
    })
  },

  onCreditsInput(e) {
    this.setData({
      'course.credits': e.detail.value
    })
  },

  // 选择器处理
  onWeekDayChange(e) {
    const index = e.detail.value
    this.setData({
      'course.week_day': this.data.weekDays[index].value
    })
  },

  onTimeSlotChange(e) {
    const index = e.detail.value
    const timeSlot = this.data.timeSlots[index].value.split('-')
    this.setData({
      'course.start_time': timeSlot[0],
      'course.end_time': timeSlot[1]
    })
  },

  onCourseTypeChange(e) {
    const index = e.detail.value
    this.setData({
      'course.course_type': this.data.courseTypes[index]
    })
  },

  // 保存课程
  saveCourse() {
    const course = this.data.course
    
    // 验证必填字段
    if (!course.course_name || !course.teacher || !course.classroom) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      })
      return
    }

    wx.showLoading({
      title: '保存中...'
    })

    // 模拟保存过程
    setTimeout(() => {
      wx.hideLoading()
      
      // 保存到本地存储
      let customCourses = wx.getStorageSync('customCourses') || []
      
      if (this.data.isEdit) {
        // 编辑模式：更新现有课程
        const index = customCourses.findIndex(c => c.id === this.data.courseId)
        if (index !== -1) {
          customCourses[index] = { ...course, id: this.data.courseId }
        }
      } else {
        // 新增模式：添加新课程
        const newCourse = {
          ...course,
          id: Date.now().toString(),
          created_at: new Date().toISOString()
        }
        customCourses.push(newCourse)
      }
      
      wx.setStorageSync('customCourses', customCourses)
      
      wx.showToast({
        title: '保存成功',
        icon: 'success'
      })
      
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }, 1000)
  },

  // 删除课程
  deleteCourse() {
    if (!this.data.isEdit) return
    
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这门课程吗？',
      success: (res) => {
        if (res.confirm) {
          let customCourses = wx.getStorageSync('customCourses') || []
          customCourses = customCourses.filter(c => c.id !== this.data.courseId)
          wx.setStorageSync('customCourses', customCourses)
          
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          })
          
          setTimeout(() => {
            wx.navigateBack()
          }, 1500)
        }
      }
    })
  },

  // 预览课程
  previewCourse() {
    const course = this.data.course
    const weekDay = this.data.weekDays.find(w => w.value === course.week_day)?.label || '周一'
    
    wx.showModal({
      title: '课程预览',
      content: `课程名称：${course.course_name}\n授课教师：${course.teacher}\n上课地点：${course.classroom}\n上课时间：${weekDay} ${course.start_time}-${course.end_time}\n上课周次：第${course.weeks}周\n课程类型：${course.course_type}\n学分：${course.credits}`,
      showCancel: false,
      confirmText: '知道了'
    })
  }
}) 