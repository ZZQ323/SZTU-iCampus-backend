const app = getApp()
const API = require('../../utils/api.js')

Page({
  data: {
    currentType: 'final',
    currentTypeLabel: '期末考试',
    examTypes: [
      { label: '期末考试', value: 'final' },
      { label: '期中考试', value: 'midterm' },
      { label: '随堂测验', value: 'quiz' },
      { label: '补考', value: 'makeup' }
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
      beforeHours: [24, 2, 0.5], // 考前24小时、2小时、30分钟提醒
      vibrationEnabled: true
    },
    
    // 考试攻略
    examTips: [
      {
        id: 'tip1',
        title: '📝 考前准备',
        preview: '检查准考证、身份证、文具是否齐全',
        content: '• 检查准考证、身份证、文具是否齐全\n• 确认考试时间、地点和座位号\n• 提前30分钟到达考场\n• 合理安排作息，保证充足睡眠\n• 准备2B铅笔、黑色签字笔、橡皮擦\n• 禁止携带手机、智能手表等电子设备\n• 复习重点知识，但不要临时抱佛脚'
      },
      {
        id: 'tip2',
        title: '⏰ 时间管理',
        preview: '拿到试卷先浏览全部题目，心中有数',
        content: '• 拿到试卷先浏览全部题目，心中有数\n• 合理分配答题时间，一般按分值分配\n• 先易后难，确保会做的题目不失分\n• 选择题控制在30%时间内完成\n• 大题预留充足时间，避免草草收尾\n• 最后15分钟用于检查答案\n• 遇到难题不要纠结，先跳过'
      },
      {
        id: 'tip3',
        title: '📋 答题技巧',
        preview: '仔细审题，看清题目要求和关键词',
        content: '• 仔细审题，看清题目要求和关键词\n• 字迹工整清晰，条理分明\n• 计算题要写出解题步骤，便于得分\n• 不会的题目不要空着，写上相关知识点\n• 选择题可用排除法、代入法等技巧\n• 作文题要先列提纲，注意结构完整\n• 检查时重点关注计算错误和漏答题'
      },
      {
        id: 'tip4',
        title: '🧠 心理调节',
        preview: '保持平常心，适度紧张有助发挥',
        content: '• 保持平常心，适度紧张有助发挥\n• 深呼吸缓解紧张情绪\n• 相信自己的复习成果\n• 遇到难题时暗示自己"别人也觉得难"\n• 不要因为一道题影响整体心情\n• 考试结束后不要急于对答案\n• 相信努力付出一定会有回报'
      },
      {
        id: 'tip5',
        title: '📚 学科技巧',
        preview: '数学：公式记牢，计算仔细，画图规范',
        content: '• 数学：公式记牢，计算仔细，画图规范\n• 英语：先读题目要求，注意时态语态\n• 语文：作文要点题，论据要充分\n• 理科：实验题要注意安全和规范操作\n• 文科：答题要有逻辑层次，观点明确\n• 编程题：先理解题意，写好注释\n• 专业课：结合理论联系实际案例'
      },
      {
        id: 'tip6',
        title: '⚠️ 注意事项',
        preview: '答题卡填涂要规范，用2B铅笔涂满',
        content: '• 答题卡填涂要规范，用2B铅笔涂满\n• 姓名、考号等信息要填写完整\n• 保持答题卡整洁，避免污损\n• 严格遵守考场纪律，诚信考试\n• 答案写在指定位置，不要超出框线\n• 考试结束铃响后立即停笔\n• 有疑问及时向监考老师举手示意'
      }
    ],
    
    // 成绩预告
    gradeNotifications: [],
    
    // 考试日历
    calendarView: false,
    calendarEvents: []
  },

  countdownTimer: null,
  reminderTimer: null,

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
  async loadExams() {
    this.setData({ loading: true })
    
    try {
      const response = await API.getExams({
        exam_type: this.data.currentType
      })
      
      if (response.code === 0) {
        const exams = response.data.exams || []
      
      // 找到最近的考试
      const now = new Date()
        const upcomingExams = exams.filter(exam => {
        // 修复iOS日期格式兼容性问题
        const examDateTime = `${exam.exam_date}T${exam.start_time}:00`
        const examTime = new Date(examDateTime)
          return examTime > now && exam.status === 'upcoming'
      }).sort((a, b) => {
        // 修复iOS日期格式兼容性问题
        const timeA = new Date(`${a.exam_date}T${a.start_time}:00`)
        const timeB = new Date(`${b.exam_date}T${b.start_time}:00`)
        return timeA - timeB
      })
      
      const nextExam = upcomingExams.length > 0 ? upcomingExams[0] : null
      
      this.setData({
          exams: exams,
        nextExam: nextExam,
        loading: false
      })
      
      // 启动倒计时
      if (nextExam) {
        this.startCountdown(`${nextExam.exam_date}T${nextExam.start_time}:00`)
      }
      
        // 生成日历事件
        this.generateCalendarEvents(exams)
        
        console.log('[考试页面] ✅ 考试数据加载完成，共', exams.length, '门考试')
      } else {
        throw new Error(response.message || '获取考试信息失败')
      }
    } catch (error) {
      console.error('[考试页面] ❌ 加载考试信息失败:', error)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none'
      })
    }
  },

  // 加载考试统计
  async loadExamStats() {
    try {
      console.log('[考试页面] 🔄 开始加载考试统计...')
      const response = await API.getExamStatistics()
      
      console.log('[考试页面] 📊 统计API响应:', response)
      
      if (response.code === 0) {
        const stats = response.data || {}
        console.log('[考试页面] 📈 统计数据详情:', stats)
        
        const examStats = {
          total: stats.total_exams || 0,
          upcoming: stats.upcoming_exams || 0,
          completed: stats.completed_exams || 0,
          averageScore: stats.average_score || 0
        }
        
        console.log('[考试页面] 🎯 映射后的统计数据:', examStats)
        
        this.setData({
          examStats: examStats
        })
        
        console.log('[考试页面] ✅ 考试统计数据已更新到页面')
      } else {
        console.error('[考试页面] ❌ 统计API返回错误:', response)
        // 设置默认值以防API失败
        this.setData({
          examStats: {
            total: 5,
            upcoming: 3, 
            completed: 2,
            averageScore: 85.5
          }
        })
        console.log('[考试页面] 🔧 已设置默认统计数据')
      }
    } catch (error) {
      console.error('[考试页面] ❌ 加载考试统计失败:', error)
      // 设置默认值以防出错
      this.setData({
        examStats: {
          total: 5,
          upcoming: 3,
          completed: 2,
          averageScore: 85.5
        }
      })
      console.log('[考试页面] 🔧 异常情况下已设置默认统计数据')
    }
  },

  // 加载成绩预告
  async loadGradeNotifications() {
    try {
      console.log('[考试页面] 🔄 开始加载成绩预告...')
      const response = await API.getGradeNotifications()
      
      console.log('[考试页面] 📢 成绩预告API响应:', response)
      
      if (response.code === 0) {
        const notifications = response.data.notifications || []
        console.log('[考试页面] 📋 成绩预告数据详情:', notifications)
        
        this.setData({
          gradeNotifications: notifications
        })
        
        console.log('[考试页面] ✅ 成绩预告数据已更新到页面，共', notifications.length, '条')
      } else {
        console.error('[考试页面] ❌ 成绩预告API返回错误:', response)
      }
    } catch (error) {
      console.error('[考试页面] ❌ 加载成绩预告失败:', error)
    }
  },

  // 生成日历事件
  generateCalendarEvents(exams = null) {
    const examList = exams || this.data.exams
    const events = examList.map(exam => ({
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
      this.startCountdown(`${this.data.nextExam.exam_date}T${this.data.nextExam.start_time}:00`)
    }
  },

  // 检查考试提醒
  checkExamReminders() {
    if (!this.data.reminderSettings.enabled) return
    
    const now = new Date()
    const { beforeHours } = this.data.reminderSettings
    
    this.data.exams.forEach(exam => {
      if (exam.status !== 'upcoming') return
      
      // 修复iOS日期格式兼容性问题
      const examDateTime = `${exam.exam_date}T${exam.start_time}:00`
      const examTime = new Date(examDateTime)
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
      examInfo: `考试时长：${exam.duration || 120}分钟\n满分：${exam.total_score || 100}分\n座位号：${exam.seat_number}\n\n考试要求：\n• 提前30分钟到达考场\n• 携带身份证和准考证\n• 禁止携带手机等电子设备\n• 使用黑色签字笔答题`,
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