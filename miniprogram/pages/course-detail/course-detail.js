const app = getApp()

Page({
  data: {
    course: {},
    loading: true
  },

  onLoad(options) {
    console.log('[课程详情] 页面加载')
    this.loadCourseDetail(options)
  },

  loadCourseDetail(options) {
    // 从全局数据中获取课程信息
    const course = app.globalData.currentCourse
    
    if (course) {
      this.setData({
        course: {
          ...course,
          // 添加课程类型中文显示
          typeText: this.getCourseTypeText(course.type),
          // 格式化时间显示
          timeText: this.formatTimeText(course)
        },
        loading: false
      })
      
      console.log('[课程详情] 课程数据加载完成:', course.name)
    } else {
      // 如果没有课程数据，返回上一页
      wx.showToast({
        title: '课程数据丢失',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  // 获取课程类型文本
  getCourseTypeText(type) {
    const typeMap = {
      required: '必修课',
      elective: '选修课',
      lab: '实验课',
      practice: '实践课'
    }
    return typeMap[type] || '其他课程'
  },

  // 格式化时间文本
  formatTimeText(course) {
    if (course.timeRange) {
      return course.timeRange
    }
    // 如果有其他时间格式，可以在这里处理
    return '时间待定'
  },

  // 复制课程信息
  copyCourseInfo() {
    const { course } = this.data
    const courseInfo = `课程：${course.name}\n教师：${course.teacher}\n地点：${course.location}\n类型：${course.typeText}\n时间：${course.timeText}`
    
    wx.setClipboardData({
      data: courseInfo,
      success: () => {
        wx.showToast({
          title: '课程信息已复制',
          icon: 'success'
        })
      }
    })
  },

  // 分享课程
  shareCourse() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })

    wx.showToast({
      title: '分享功能已开启',
      icon: 'success'
    })
  }
}) 