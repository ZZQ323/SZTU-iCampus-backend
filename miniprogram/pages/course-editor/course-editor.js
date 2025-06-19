const app = getApp()

Page({
  data: {
    isEdit: false,
    submitting: false,
    
    // 表单数据
    form: {
      course_name: '',
      course_code: '',
      teacher: '',
      classroom: '',
      week_day: 1,
      time_slot: 1,
      start_time: '08:30',
      end_time: '10:10',
      week_expression: '1-16',
      start_week: 1,
      end_week: 16,
      odd_even: 'all',
      course_type: '必修',
      credits: '',
      course_hours: 32,
      course_description: '',
      textbook: '',
      semester: '2024-2025-1',
      academic_year: '2024-2025',
      term: 1,
      student_id: '',
      class_name: '',
      major: '',
      college: ''
    },
    
    // 选择器数据
    weekDayOptions: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    timeSlotOptions: ['第1-2节', '第3-4节', '第5-6节', '第7-8节', '第9-10节'],
    
    // 选择器弹窗
    showWeekDayPicker: false,
    showTimeSlotPicker: false,
    weekDayPickerOptions: [],
    timeSlotPickerOptions: [],
    
    // 用户信息
    userInfo: {}
  },

  onLoad(options) {
    this.getUserInfo()
    this.initializeForm()
    this.initializePickers()
    
    // 判断是编辑还是新增
    if (options.id) {
      this.setData({ isEdit: true })
      this.loadCourseData(options.id)
    } else {
      // 新增课程，设置默认位置
      this.setDefaultPosition()
    }
  },

  // 获取用户信息
  getUserInfo() {
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({ 
        userInfo,
        'form.student_id': userInfo.student_id,
        'form.class_name': userInfo.class_name || '',
        'form.major': userInfo.major || '',
        'form.college': userInfo.college || ''
      })
    }
  },

  // 初始化表单
  initializeForm() {
    // 设置默认的时间段
    const timeSlots = [
      { start_time: '08:30', end_time: '10:10' },
      { start_time: '10:30', end_time: '12:10' },
      { start_time: '14:00', end_time: '15:40' },
      { start_time: '16:00', end_time: '17:40' },
      { start_time: '19:00', end_time: '20:40' }
    ]
    
    this.setData({
      'form.start_time': timeSlots[0].start_time,
      'form.end_time': timeSlots[0].end_time
    })
  },

  // 初始化选择器
  initializePickers() {
    const weekDayPickerOptions = this.data.weekDayOptions.map((label, index) => ({
      label,
      value: index + 1
    }))
    
    const timeSlotPickerOptions = this.data.timeSlotOptions.map((label, index) => ({
      label,
      value: index + 1
    }))
    
    this.setData({
      weekDayPickerOptions,
      timeSlotPickerOptions
    })
  },

  // 设置默认位置（从课表页面传递的位置信息）
  setDefaultPosition() {
    const position = app.globalData.addCoursePosition
    if (position) {
      this.setData({
        'form.week_day': position.weekDay,
        'form.time_slot': position.timeSlot,
        'form.semester': position.semester
      })
      
      // 更新时间
      this.updateTimeBySlot(position.timeSlot)
    }
  },

  // 根据时间段更新开始结束时间
  updateTimeBySlot(timeSlot) {
    const timeSlots = [
      { start_time: '08:30', end_time: '10:10' },
      { start_time: '10:30', end_time: '12:10' },
      { start_time: '14:00', end_time: '15:40' },
      { start_time: '16:00', end_time: '17:40' },
      { start_time: '19:00', end_time: '20:40' }
    ]
    
    const slot = timeSlots[timeSlot - 1]
    if (slot) {
      this.setData({
        'form.start_time': slot.start_time,
        'form.end_time': slot.end_time
      })
    }
  },

  // 加载课程数据（编辑模式）
  loadCourseData(courseId) {
    const token = wx.getStorageSync('token')
    
    wx.request({
      url: `${app.globalData.baseURL}/api/v1/schedule/${courseId}`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            form: { ...this.data.form, ...res.data }
          })
        } else {
          console.error('加载课程失败:', res)
          wx.showToast({
            title: '加载课程失败',
            icon: 'none'
          })
        }
      },
      fail: (error) => {
        console.error('加载课程失败:', error)
        wx.showToast({
          title: '加载课程失败',
          icon: 'none'
        })
      }
    })
  },

  // 通用字段变化处理
  onFieldChange(e) {
    const field = e.currentTarget.dataset.field
    const value = e.detail.value
    
    this.setData({
      [`form.${field}`]: value
    })
    
    // 特殊处理：周次表达式变化时更新开始结束周次
    if (field === 'week_expression') {
      this.parseWeekExpression(value)
    }
  },

  // 数字步进器变化处理
  onStepperChange(e) {
    const field = e.currentTarget.dataset.field
    const value = e.detail.value
    
    this.setData({
      [`form.${field}`]: value
    })
  },

  // 单双周变化
  onOddEvenChange(e) {
    this.setData({
      'form.odd_even': e.detail.value
    })
  },

  // 课程类型变化
  onCourseTypeChange(e) {
    this.setData({
      'form.course_type': e.detail.value
    })
  },

  // 解析周次表达式
  parseWeekExpression(expression) {
    if (!expression) return
    
    try {
      // 简单解析：1-16 格式
      if (expression.includes('-') && !expression.includes(',')) {
        const [start, end] = expression.split('-').map(num => parseInt(num.trim()))
        if (!isNaN(start) && !isNaN(end) && start <= end) {
          this.setData({
            'form.start_week': start,
            'form.end_week': end
          })
        }
      }
    } catch (error) {
      console.log('解析周次表达式失败:', error)
    }
  },

  // 选择星期
  selectWeekDay() {
    this.setData({ showWeekDayPicker: true })
  },

  hideWeekDayPicker() {
    this.setData({ showWeekDayPicker: false })
  },

  onWeekDaySelect(e) {
    const weekDay = e.detail.value
    this.setData({
      'form.week_day': weekDay,
      showWeekDayPicker: false
    })
  },

  // 选择时间段
  selectTimeSlot() {
    this.setData({ showTimeSlotPicker: true })
  },

  hideTimeSlotPicker() {
    this.setData({ showTimeSlotPicker: false })
  },

  onTimeSlotSelect(e) {
    const timeSlot = e.detail.value
    this.setData({
      'form.time_slot': timeSlot,
      showTimeSlotPicker: false
    })
    
    // 更新对应的时间
    this.updateTimeBySlot(timeSlot)
  },

  // 表单验证
  validateForm() {
    const { form } = this.data
    
    if (!form.course_name?.trim()) {
      wx.showToast({ title: '请输入课程名称', icon: 'none' })
      return false
    }
    
    if (!form.teacher?.trim()) {
      wx.showToast({ title: '请输入教师姓名', icon: 'none' })
      return false
    }
    
    if (!form.classroom?.trim()) {
      wx.showToast({ title: '请输入教室', icon: 'none' })
      return false
    }
    
    if (form.start_week > form.end_week) {
      wx.showToast({ title: '开始周次不能大于结束周次', icon: 'none' })
      return false
    }
    
    return true
  },

  // 保存课程
  onSave() {
    if (!this.validateForm()) return
    
    this.setData({ submitting: true })
    
    const token = wx.getStorageSync('token')
    const url = this.data.isEdit 
      ? `${app.globalData.baseURL}/api/v1/schedule/${this.data.form.id}`
      : `${app.globalData.baseURL}/api/v1/schedule/`
    
    const method = this.data.isEdit ? 'PUT' : 'POST'
    
    wx.request({
      url,
      method,
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: this.data.form,
      success: (res) => {
        console.log('保存课程响应:', res)
        
        if (res.statusCode === 200) {
          wx.showToast({
            title: this.data.isEdit ? '更新成功' : '保存成功',
            icon: 'success'
          })
          
          setTimeout(() => {
            wx.navigateBack()
          }, 1500)
        } else {
          console.error('保存失败:', res)
          wx.showToast({
            title: res.data?.detail || '操作失败',
            icon: 'none'
          })
        }
        
        this.setData({ submitting: false })
      },
      fail: (error) => {
        console.error('保存失败:', error)
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        
        this.setData({ submitting: false })
      }
    })
  },

  // 取消
  onCancel() {
    wx.showModal({
      title: '确认取消',
      content: '确定要取消编辑吗？未保存的内容将丢失',
      success: (res) => {
        if (res.confirm) {
          wx.navigateBack()
        }
      }
    })
  }
}) 