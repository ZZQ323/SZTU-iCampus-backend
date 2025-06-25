const app = getApp()
const API = require('../../utils/api.js')

Page({
  data: {
    exam: {},
    loading: true,
    
    // 考试详细信息
    examDetail: {
      duration: 120,
      totalScore: 100,
      examType: 'written',
      materials: ['身份证', '准考证', '黑色签字笔', '2B铅笔', '橡皮擦'],
      prohibited: ['手机', '智能手表', '计算器', '书籍', '笔记']
    },
    
    // 座位信息
    seatInfo: {
      building: '',
      room: '',
      seat: '',
      floor: '',
      mapUrl: ''
    },
    
    // 提醒设置
    reminderEnabled: false,
    
    // 考试进度
    examProgress: {
      registration: true,
      preparation: false,
      examination: false,
      completed: false
    }
  },

  onLoad(options) {
    console.log('[考试详情] 页面加载')
    
    // 从全局数据或URL参数获取考试信息
    if (app.globalData.currentExam) {
      this.setData({
        exam: app.globalData.currentExam,
        loading: false
      })
      this.loadExamDetail()
    } else if (options.examId) {
      this.loadExamById(options.examId)
    } else {
      wx.showToast({
        title: '考试信息获取失败',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 2000)
    }
  },

  onShow() {
    console.log('[考试详情] 页面显示')
  },

  // 根据ID加载考试详情
  async loadExamById(examId) {
    this.setData({ loading: true })
    
    try {
      const response = await API.getExamDetail(examId)
      
      if (response.code === 0) {
        this.setData({
          exam: response.data,
          loading: false
        })
        this.loadExamDetail()
      } else {
        throw new Error(response.message || '获取考试详情失败')
      }
    } catch (error) {
      console.error('[考试详情] ❌ 加载考试详情失败:', error)
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none'
      })
      this.setData({ loading: false })
    }
  },

  // 加载考试详细信息
  loadExamDetail() {
    const { exam } = this.data
    
    // 解析座位信息
    const seatInfo = this.parseSeatInfo(exam.location, exam.seat_number)
    
    // 检查考试进度
    const progress = this.calculateExamProgress(exam)
    
    // 检查提醒设置
    const reminderEnabled = this.checkReminderStatus(exam.exam_id)
    
    this.setData({
      seatInfo,
      examProgress: progress,
      reminderEnabled
    })
  },

  // 解析座位信息
  parseSeatInfo(location, seatNumber) {
    const parts = location ? location.split('-') : ['', '', '']
    
    return {
      building: parts[0] || '教学楼',
      room: parts[1] || location || '考场',
      seat: seatNumber || 'A01',
      floor: parts[0] ? this.getFloorFromRoom(parts[1]) : '1',
      mapUrl: ''
    }
  },

  // 从房间号推断楼层
  getFloorFromRoom(room) {
    if (!room) return '1'
    const roomNum = parseInt(room.replace(/\D/g, ''))
    if (roomNum >= 400) return '4'
    if (roomNum >= 300) return '3'
    if (roomNum >= 200) return '2'
    return '1'
  },

  // 计算考试进度
  calculateExamProgress(exam) {
    const now = new Date()
    const examTime = new Date(`${exam.exam_date}T${exam.start_time}:00`)
    const endTime = new Date(`${exam.exam_date}T${exam.end_time}:00`)
    
    if (now > endTime) {
      return {
        registration: true,
        preparation: true,
        examination: true,
        completed: true
      }
    } else if (now > examTime) {
      return {
        registration: true,
        preparation: true,
        examination: true,
        completed: false
      }
    } else if (examTime - now < 24 * 60 * 60 * 1000) {
      return {
        registration: true,
        preparation: true,
        examination: false,
        completed: false
      }
    } else {
      return {
        registration: true,
        preparation: false,
        examination: false,
        completed: false
      }
    }
  },

  // 检查提醒状态
  checkReminderStatus(examId) {
    // 从本地存储检查提醒设置
    const reminders = wx.getStorageSync('examReminders') || []
    return reminders.includes(examId)
  },

  // 返回上一页
  onBack() {
    wx.navigateBack()
  },

  // 查看考场地图
  onViewMap() {
    const { seatInfo } = this.data
    
    wx.showModal({
      title: '考场位置',
      content: `考场位置：${seatInfo.building} ${seatInfo.room}\n座位号：${seatInfo.seat}\n楼层：${seatInfo.floor}层\n\n考场示意图：\n[前方讲台]\nA区: A01-A20\nB区: B01-B20\nC区: C01-C20\n[您的座位: ${seatInfo.seat}]`,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 设置考试提醒
  onSetReminder() {
    const { exam, reminderEnabled } = this.data
    const newStatus = !reminderEnabled
    
    if (newStatus) {
      // 开启提醒
      wx.showModal({
        title: '设置考试提醒',
        content: `确定为《${exam.course_name}》设置考前提醒？\n\n将在考前24小时、2小时和30分钟提醒您`,
        success: (res) => {
          if (res.confirm) {
            this.saveReminderSetting(exam.exam_id, true)
            this.setData({ reminderEnabled: true })
            
            wx.showToast({
              title: '提醒设置成功',
              icon: 'success'
            })
          }
        }
      })
    } else {
      // 关闭提醒
      this.saveReminderSetting(exam.exam_id, false)
      this.setData({ reminderEnabled: false })
      
      wx.showToast({
        title: '提醒已关闭',
        icon: 'success'
      })
    }
  },

  // 保存提醒设置
  saveReminderSetting(examId, enabled) {
    let reminders = wx.getStorageSync('examReminders') || []
    
    if (enabled) {
      if (!reminders.includes(examId)) {
        reminders.push(examId)
      }
    } else {
      reminders = reminders.filter(id => id !== examId)
    }
    
    wx.setStorageSync('examReminders', reminders)
  },

  // 下载准考证
  onDownloadTicket() {
    wx.showModal({
      title: '下载准考证',
      content: '准考证将保存到手机相册，请确保网络连接正常',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '生成中...' })
          
          // 模拟下载过程
          setTimeout(() => {
            wx.hideLoading()
            wx.showToast({
              title: '准考证已保存到相册',
              icon: 'success'
            })
          }, 2000)
        }
      }
    })
  },

  // 查看考试规则
  onViewRules() {
    const rules = `考试纪律要求：

📋 考前准备：
• 提前30分钟到达考场
• 携带有效身份证件和准考证
• 准备规定的考试用品

✏️ 考试期间：
• 按指定座位就座，不得随意调换
• 保持考场安静，禁止交头接耳
• 严禁携带手机等电子设备
• 答题使用黑色签字笔
• 不得在考场内吸烟或饮食

📤 考试结束：
• 停笔等待监考老师收卷
• 按顺序离开考场
• 不得将试卷带出考场

⚠️ 违纪后果：
• 作弊者成绩无效
• 情节严重者将受到纪律处分`

    wx.showModal({
      title: '考试纪律',
      content: rules,
      showCancel: false,
      confirmText: '已了解'
    })
  },

  // 查看考试材料要求
  onViewMaterials() {
    const { examDetail } = this.data
    
    const materials = `考试用品要求：

✅ 必带物品：
${examDetail.materials.map(item => `• ${item}`).join('\n')}

❌ 禁带物品：
${examDetail.prohibited.map(item => `• ${item}`).join('\n')}

📝 特殊说明：
• 草稿纸由考场提供
• 作图可使用铅笔，其他一律用黑色签字笔
• 如需计算器请确认考试是否允许`

    wx.showModal({
      title: '考试用品',
      content: materials,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 分享考试信息
  onShareExam() {
    const { exam } = this.data
    
    return {
      title: `${exam.course_name} - 考试提醒`,
      path: `/pages/exam-detail/exam-detail?examId=${exam.exam_id}`,
      imageUrl: '/assets/icons/examination.png'
    }
  },

  // 添加到日历
  onAddToCalendar() {
    const { exam } = this.data
    
    wx.showModal({
      title: '添加到日历',
      content: `将《${exam.course_name}》考试安排添加到手机日历？\n\n时间：${exam.exam_date} ${exam.start_time}\n地点：${exam.location}`,
      success: (res) => {
        if (res.confirm) {
          // 这里可以调用系统日历API
          wx.showToast({
            title: '已添加到日历',
            icon: 'success'
          })
        }
      }
    })
  }
}) 