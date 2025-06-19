const app = getApp()

Page({
  data: {
    currentWeek: 1,
    visible: false,
    schedules: [],
    loading: true,
    weekSchedule: {
      1: [], // 周一
      2: [], // 周二
      3: [], // 周三
      4: [], // 周四
      5: [], // 周五
      6: [], // 周六
      7: []  // 周日
    },
    timeSlots: [
      { label: '第1-2节', time: '08:30-10:10' },
      { label: '第3-4节', time: '10:30-12:10' },
      { label: '第5-6节', time: '14:00-15:40' },
      { label: '第7-8节', time: '16:00-17:40' },
      { label: '第9-10节', time: '19:00-20:40' }
    ],
    weekDays: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  },

  onLoad() {
    this.calculateCurrentWeek();
    this.fetchSchedule();
  },

  onShow() {
    this.fetchSchedule();
  },

  async fetchSchedule() {
    try {
      this.setData({ loading: true })
      
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/schedule`,
          method: 'GET',
          data: {
            student_id: '2024001',
            week: this.data.currentWeek
          },
          header: {
            'Content-Type': 'application/json'
          },
          success: resolve,
          fail: reject
        })
      })
      
      console.log('课表API Response:', response)
      
      if (response.statusCode === 200 && response.data.code === 0) {
        const schedules = response.data.data.schedules || []
        this.setData({
          schedules: schedules
        })
        this.organizeScheduleByWeek(schedules)
        console.log('课表数据已更新:', schedules)
      } else {
        console.error('API返回错误:', response.data)
        wx.showToast({
          title: '获取课表失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('获取课表失败:', error)
      wx.showToast({
        title: '网络连接失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  organizeScheduleByWeek(schedules) {
    const weekSchedule = {
      1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []
    }
    
    schedules.forEach(schedule => {
      if (weekSchedule[schedule.week_day]) {
        weekSchedule[schedule.week_day].push(schedule)
      }
    })
    
    // 按时间排序
    Object.keys(weekSchedule).forEach(day => {
      weekSchedule[day].sort((a, b) => a.start_time.localeCompare(b.start_time))
    })
    
    this.setData({ weekSchedule })
  },

  calculateCurrentWeek() {
    // 这里应该根据学期开始时间计算当前周次
    // 暂时使用模拟数据
    this.setData({
      currentWeek: 1
    });
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.fetchSchedule().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  onConfirm(e) {
    const { value } = e.detail;
    // 处理日期选择
    this.setData({
      visible: false
    });
    // TODO: 根据选择的日期获取课表数据
  },

  onClose() {
    this.setData({
      visible: false
    });
  },

  viewCourseDetail(e) {
    const course = e.currentTarget.dataset.course
    wx.showModal({
      title: course.course_name,
      content: `教师：${course.teacher}\n教室：${course.classroom}\n时间：${course.start_time}-${course.end_time}\n周次：${course.weeks}\n学分：${course.credits}`,
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 自定义课表
  customSchedule() {
    console.log('[课表] 打开自定义课表编辑器')
    wx.navigateTo({
      url: '/pages/schedule-editor/schedule-editor'
    })
  },

  // 导入课表
  importSchedule() {
    wx.showActionSheet({
      itemList: ['从Excel导入', '从教务系统同步', '手动输入'],
      success: (res) => {
        switch(res.tapIndex) {
          case 0:
            this.importFromExcel()
            break
          case 1:
            this.syncFromSystem()
            break
          case 2:
            this.addCourseManually()
            break
        }
      }
    })
  },

  // 从Excel导入
  importFromExcel() {
    wx.showToast({
      title: 'Excel导入功能开发中',
      icon: 'none'
    })
  },

  // 从教务系统同步
  syncFromSystem() {
    wx.showLoading({
      title: '同步中...'
    })
    
    // 模拟同步过程
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({
        title: '同步成功',
        icon: 'success'
      })
      this.fetchSchedule()
    }, 2000)
  },

  // 手动添加课程
  addCourseManually() {
    wx.navigateTo({
      url: '/pages/course-editor/course-editor'
    })
  }
}); 