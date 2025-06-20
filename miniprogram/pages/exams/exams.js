const app = getApp()

Page({
  data: {
    currentType: 'final',
    currentTypeLabel: '期末考试',
    examTypes: [
      { label: '期末考试', value: 'final' },
      { label: '期中考试', value: 'midterm' },
      { label: '补考', value: 'makeup' },
      { label: '重修考试', value: 'retake' }
    ],
    exams: [],
    nextExam: null,
    countdown: '',
    loading: true,
    
    // 考试统计
    examStats: {
      total: 0,
      upcoming: 0,
      completed: 0,
      averageScore: 0
    },
    
    // 考试提醒设置
    reminderSettings: {
      enabled: true,
      beforeHours: [24, 2], // 考前24小时和2小时提醒
      soundEnabled: true,
      vibrationEnabled: true
    },
    
    // 考试攻略
    examTips: [
      {
        id: 1,
        title: '📋 考前准备清单',
        content: '• 检查准考证、身份证\n• 准备文具用品\n• 确认考试时间地点\n• 复习重点知识点'
      },
      {
        id: 2,
        title: '⏰ 时间管理技巧',
        content: '• 提前30分钟到达考场\n• 合理分配答题时间\n• 先易后难，不要纠结\n• 预留检查时间'
      },
      {
        id: 3,
        title: '🧘 心理调节方法',
        content: '• 保持充足睡眠\n• 适度运动放松\n• 深呼吸缓解紧张\n• 积极暗示增强信心'
      }
    ],
    
    // 成绩预告
    gradeNotifications: [],
    
    // 考试日历
    calendarView: false,
    calendarEvents: []
  },

  onLoad() {
    console.log('[考试页面] 📝 页面加载')
    this.loadAllData()
    this.initReminders()
  },

  onShow() {
    console.log('[考试页面] 页面显示')
    this.refreshExamData()
  },

  onUnload() {
    console.log('[考试页面] 页面卸载')
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
    }
    if (this.reminderTimer) {
      clearInterval(this.reminderTimer)
    }
  },

  onPullDownRefresh() {
    console.log('[考试页面] 🔄 下拉刷新')
    this.loadAllData()
    
    setTimeout(() => {
      wx.stopPullDownRefresh()
      wx.showToast({
        title: '刷新完成',
        icon: 'success'
      })
    }, 1500)
  },

  // 加载所有数据
  loadAllData() {
    this.loadExams()
    this.loadExamStats()
    this.loadGradeNotifications()
    this.generateCalendarEvents()
  },

  // 刷新考试数据
  refreshExamData() {
    this.loadExams()
    this.updateCountdown()
  },

  // 初始化提醒功能
  initReminders() {
    // 检查提醒权限
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.userInfo']) {
          console.log('[考试页面] 需要用户授权通知权限')
        }
      }
    })
    
    // 启动提醒检查定时器
    this.reminderTimer = setInterval(() => {
      this.checkExamReminders()
    }, 60000) // 每分钟检查一次
  },

  // 返回上一页
  onBack() {
    wx.navigateBack()
  },

  // 考试类型切换
  onTypeChange(e) {
    const { value } = e.detail
    console.log('[考试页面] 🏷️ 切换考试类型:', value)
    
    // 找到对应的标签
    const typeInfo = this.data.examTypes.find(t => t.value === value)
    const typeLabel = typeInfo ? typeInfo.label : '考试'
    
    this.setData({
      currentType: value,
      currentTypeLabel: typeLabel
    })
    this.loadExams()
  },

  // 加载考试信息
  loadExams() {
    this.setData({ loading: true })
    
    const userInfo = wx.getStorageSync('userInfo')
    const studentId = userInfo?.studentId || '2024001'
    
    // 模拟API请求
    setTimeout(() => {
      const mockExams = this.generateMockExams()
      
      // 找到最近的考试
      const now = new Date()
      const upcomingExams = mockExams.filter(exam => {
        const examTime = new Date(`${exam.exam_date} ${exam.start_time}`)
        return examTime > now
      }).sort((a, b) => {
        const timeA = new Date(`${a.exam_date} ${a.start_time}`)
        const timeB = new Date(`${b.exam_date} ${b.start_time}`)
        return timeA - timeB
      })
      
      const nextExam = upcomingExams.length > 0 ? upcomingExams[0] : null
      
      this.setData({
        exams: mockExams,
        nextExam: nextExam,
        loading: false
      })
      
      // 启动倒计时
      if (nextExam) {
        this.startCountdown(`${nextExam.exam_date} ${nextExam.start_time}`)
      }
      
      console.log('[考试页面] ✅ 考试数据加载完成，共', mockExams.length, '门考试')
    }, 1000)
  },

  // 生成模拟考试数据
  generateMockExams() {
    const baseExams = [
      {
        id: 1,
        course_name: '高等数学A',
        course_code: 'MATH1001',
        exam_date: '2024-06-25',
        start_time: '09:00',
        end_time: '11:00',
        location: 'C1-101',
        seat_number: 'A15',
        instructor: '张教授',
        exam_type: 'final',
        status: 'upcoming',
        duration: 120,
        totalScore: 100,
        tips: '重点复习微积分和线性代数'
      },
      {
        id: 2,
        course_name: '计算机网络',
        course_code: 'CS2001',
        exam_date: '2024-06-27',
        start_time: '14:00',
        end_time: '16:00',
        location: 'C2-203',
        seat_number: 'B08',
        instructor: '李教授',
        exam_type: 'final',
        status: 'upcoming',
        duration: 120,
        totalScore: 100,
        tips: '重点复习TCP/IP协议和网络安全'
      },
      {
        id: 3,
        course_name: '数据结构',
        course_code: 'CS1002',
        exam_date: '2024-06-22',
        start_time: '10:00',
        end_time: '12:00',
        location: 'C1-205',
        seat_number: 'C12',
        instructor: '王教授',
        exam_type: 'final',
        status: 'completed',
        duration: 120,
        totalScore: 100,
        score: 88,
        tips: '重点复习树和图的算法'
      }
    ]
    
    // 根据当前选择的考试类型过滤
    return baseExams.filter(exam => exam.exam_type === this.data.currentType)
  },

  // 加载考试统计
  loadExamStats() {
    const stats = {
      total: 8,
      upcoming: 3,
      completed: 5,
      averageScore: 85.6
    }
    
    this.setData({
      examStats: stats
    })
  },

  // 加载成绩预告
  loadGradeNotifications() {
    const mockNotifications = [
      {
        id: 1,
        course: '数据结构',
        message: '成绩已发布，点击查看',
        time: '2024-06-20 15:30',
        type: 'grade_published'
      },
      {
        id: 2,
        course: '操作系统',
        message: '成绩将于明日公布',
        time: '2024-06-19 10:00',
        type: 'grade_coming'
      }
    ]
    
    this.setData({
      gradeNotifications: mockNotifications
    })
  },

  // 生成日历事件
  generateCalendarEvents() {
    const events = this.data.exams.map(exam => ({
      date: exam.exam_date,
      title: exam.course_name,
      time: `${exam.start_time}-${exam.end_time}`,
      location: exam.location,
      type: 'exam'
    }))
    
    this.setData({
      calendarEvents: events
    })
  },

  // 启动倒计时
  startCountdown(examTime) {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
    }
    
    const updateCountdown = () => {
      const now = new Date()
      const exam = new Date(examTime)
      const diff = exam - now

      if (diff <= 0) {
        this.setData({ countdown: '考试已开始' })
        clearInterval(this.countdownTimer)
        return
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)

      let countdownText = ''
      if (days > 0) {
        countdownText = `${days}天${hours}小时${minutes}分`
      } else if (hours > 0) {
        countdownText = `${hours}小时${minutes}分${seconds}秒`
      } else {
        countdownText = `${minutes}分${seconds}秒`
      }

      this.setData({
        countdown: countdownText
      })
    }

    updateCountdown()
    this.countdownTimer = setInterval(updateCountdown, 1000)
  },

  // 更新倒计时
  updateCountdown() {
    if (this.data.nextExam) {
      this.startCountdown(`${this.data.nextExam.exam_date} ${this.data.nextExam.start_time}`)
    }
  },

  // 检查考试提醒
  checkExamReminders() {
    if (!this.data.reminderSettings.enabled) return
    
    const now = new Date()
    const { beforeHours } = this.data.reminderSettings
    
    this.data.exams.forEach(exam => {
      if (exam.status !== 'upcoming') return
      
      const examTime = new Date(`${exam.exam_date} ${exam.start_time}`)
      const timeDiff = examTime - now
      const hoursDiff = timeDiff / (1000 * 60 * 60)
      
      beforeHours.forEach(hours => {
        // 检查是否需要提醒（误差范围1分钟）
        if (Math.abs(hoursDiff - hours) < 0.017) {
          this.sendExamReminder(exam, hours)
        }
      })
    })
  },

  // 发送考试提醒
  sendExamReminder(exam, hours) {
    const message = hours >= 24 ? 
      `📝 考试提醒：${exam.course_name}将在明天${exam.start_time}开始，地点：${exam.location}` :
      `📝 考试提醒：${exam.course_name}将在${hours}小时后开始，请做好准备！`
    
    wx.showModal({
      title: '考试提醒',
      content: message,
      showCancel: true,
      cancelText: '知道了',
      confirmText: '查看详情',
      success: (res) => {
        if (res.confirm) {
          this.onViewDetail({ currentTarget: { dataset: { exam } } })
        }
      }
    })
    
    // 震动提醒
    if (this.data.reminderSettings.vibrationEnabled) {
      wx.vibrateShort()
    }
  },

  // 查看考试详情
  onViewDetail(e) {
    const exam = e.currentTarget.dataset.exam
    console.log('[考试页面] 📋 查看考试详情:', exam.course_name)
    
    // 构造详情数据
    const examDetail = {
      ...exam,
      examInfo: `考试时长：${exam.duration}分钟\n满分：${exam.totalScore}分\n座位号：${exam.seat_number}\n\n考试要求：\n• 提前30分钟到达考场\n• 携带身份证和准考证\n• 禁止携带手机等电子设备\n• 使用黑色签字笔答题`,
      preparationTips: exam.tips || '暂无特殊提示'
    }
    
    // 存储到全局数据
    app.globalData.currentExam = examDetail
    
    wx.navigateTo({
      url: '/pages/exam-detail/exam-detail'
    })
  },

  // 设置考试提醒
  onSetReminder(e) {
    const exam = e.currentTarget.dataset.exam
    
    wx.showModal({
      title: '考试提醒设置',
      content: `为《${exam.course_name}》设置考前提醒？\n\n将在考前24小时和2小时提醒您`,
      success: (res) => {
        if (res.confirm) {
          wx.showToast({
            title: '提醒设置成功',
            icon: 'success'
          })
          
          // 这里可以调用后端API设置提醒
          console.log('[考试页面] 🔔 设置考试提醒:', exam.course_name)
        }
      }
    })
  },

  // 查看座位信息
  onViewSeat(e) {
    const exam = e.currentTarget.dataset.exam
    
    const seatInfo = `考试座位信息：

📍 考场：${exam.location}
💺 座位：${exam.seat_number}
⏰ 时间：${exam.exam_date} ${exam.start_time}-${exam.end_time}

考场示意图：
[前方讲台]
A01 A02 A03 ... A20
B01 B02 B03 ... B20
C01 C02 C03 ... C20
[您的座位: ${exam.seat_number}]

注意事项：
• 按座位号就座，不得随意调换
• 考试用品放在桌面右上角
• 保持考场安静，禁止交头接耳`

    wx.showModal({
      title: '座位信息',
      content: seatInfo,
      showCancel: false,
      confirmText: '知道了',
      confirmColor: '#0052d9'
    })
  },

  // 查看考试攻略
  onViewTips(e) {
    const tip = e.currentTarget.dataset.tip
    
    wx.showModal({
      title: tip.title,
      content: tip.content,
      showCancel: false,
      confirmText: '收藏了',
      confirmColor: '#0052d9'
    })
  },

  // 切换日历视图
  onToggleCalendar() {
    this.setData({
      calendarView: !this.data.calendarView
    })
  },

  // 提醒设置
  onReminderSettings() {
    const { reminderSettings } = this.data
    
    wx.showActionSheet({
      itemList: [
        `提醒功能：${reminderSettings.enabled ? '已开启' : '已关闭'}`,
        `震动提醒：${reminderSettings.vibrationEnabled ? '已开启' : '已关闭'}`,
        '提醒时间设置',
        '查看所有提醒'
      ],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            this.toggleReminder()
            break
          case 1:
            this.toggleVibration()
            break
          case 2:
            this.setReminderTime()
            break
          case 3:
            this.viewAllReminders()
            break
        }
      }
    })
  },

  // 切换提醒开关
  toggleReminder() {
    const enabled = !this.data.reminderSettings.enabled
    
    this.setData({
      'reminderSettings.enabled': enabled
    })
    
    wx.showToast({
      title: enabled ? '提醒已开启' : '提醒已关闭',
      icon: 'success'
    })
  },

  // 切换震动开关
  toggleVibration() {
    const enabled = !this.data.reminderSettings.vibrationEnabled
    
    this.setData({
      'reminderSettings.vibrationEnabled': enabled
    })
    
    wx.showToast({
      title: enabled ? '震动已开启' : '震动已关闭',
      icon: 'success'
    })
  },

  // 设置提醒时间
  setReminderTime() {
    wx.showModal({
      title: '提醒时间设置',
      content: '当前设置：考前24小时和2小时提醒\n\n是否修改提醒时间？',
      success: (res) => {
        if (res.confirm) {
          // 这里可以实现更详细的时间设置界面
          wx.showToast({
            title: '功能开发中',
            icon: 'none'
          })
        }
      }
    })
  },

  // 查看所有提醒
  viewAllReminders() {
    wx.navigateTo({
      url: '/pages/exam-reminders/exam-reminders'
    })
  }
}) 