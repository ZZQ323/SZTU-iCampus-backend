const { BasePage, createPage } = require('../../utils/BasePage')

class GradesPage extends BasePage {
  getPageName() {
    return '成绩查询'
  }

  getInitialData() {
    return {
      gradesData: {
        semester_info: {
          current_semester: "2024-2025-1",
          academic_year: "2024-2025"
        },
        summary: {
          total_courses: 0,
          total_credits: 0,
          avg_score: 0,
          gpa: 0
        },
        grades: []
      },
      semesterRange: [
        {label: "2024-2025学年 第一学期", value: "2024-2025-1"},
        {label: "2023-2024学年 第二学期", value: "2023-2024-2"},
        {label: "2023-2024学年 第一学期", value: "2023-2024-1"}
      ],
      semesterIndex: 0,
      currentFilter: 'all',
      filteredGrades: [],
      showModal: false,
      modalData: {},
      loading: false
    }
  }

  requiresLogin() {
    return true
  }

  async loadInitialData(options) {
    console.log('📊 成绩查询页面加载')
    await this.loadGradesData()
    this.applyFilter()
  }

  async refreshData(force = false) {
    await this.loadGradesData()
  }

  async loadGradesData() {
    try {
      this.setData({ loading: true })
      
      const API = require('../../utils/api')
      const gradesResponse = await API.getGrades({
        semester: this.data.gradesData.semester_info.current_semester
      })
      
      console.log('✅ 成绩数据:', gradesResponse)
      
      if (gradesResponse && gradesResponse.code === 0) {
        const gradesData = gradesResponse.data
        
        this.setData({
          'gradesData.semester_info': gradesData.semester_info || this.data.gradesData.semester_info,
          'gradesData.grades': gradesData.grades || [],
          'gradesData.summary': gradesData.summary || this.data.gradesData.summary,
          'gradesData.semesterDisplayName': this.formatSemesterDisplay(gradesData.semester_info?.current_semester)
        })
        
        this.applyFilter()
      }
      
    } catch (error) {
      console.error('❌ 加载成绩失败:', error)
      this.showToast('加载失败', 'error')
    } finally {
      this.setData({ loading: false })
    }
  }

  onSemesterChange(e) {
    const semesterIndex = e.detail.value
    const semester = this.data.semesterRange[semesterIndex].value
    
    this.setData({
      semesterIndex,
      'gradesData.semester_info.current_semester': semester,
      'gradesData.semesterDisplayName': this.formatSemesterDisplay(semester)
    })
    
    this.loadGradesData()
  }

  setFilter(e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({ currentFilter: filter })
    this.applyFilter()
  }

  applyFilter() {
    const { currentFilter, gradesData } = this.data
    let filteredGrades = gradesData.grades
    
    if (currentFilter !== 'all') {
      filteredGrades = gradesData.grades.filter(grade => 
        grade.course_type === currentFilter
      )
    }
    
    this.setData({ filteredGrades })
  }

  showGradeDetail(e) {
    const grade = e.currentTarget.dataset.grade
    this.setData({
      showModal: true,
      modalData: grade
    })
  }

  hideModal() {
    this.setData({
      showModal: false,
      modalData: {}
    })
  }

  stopPropagation() {
    // 阻止冒泡
  }

  formatSemesterDisplay(semester) {
    if (!semester) return ''
    
    const parts = semester.split('-')
    if (parts.length === 3) {
      const startYear = parts[0]
      const endYear = parts[1]
      const semesterNum = parts[2]
      const semesterName = semesterNum === '1' ? '第一学期' : '第二学期'
      return `${startYear}-${endYear}学年 ${semesterName}`
    }
    
    return semester
  }
}

module.exports = createPage(new GradesPage()) 
