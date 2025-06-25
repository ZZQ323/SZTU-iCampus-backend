const ResourceClient = require('../ResourceClient')
const DataProcessor = require('../DataProcessor')

/**
 * 成绩客户端
 * 处理成绩相关的API操作
 * 包括成绩查询、统计分析、GPA计算、趋势分析等
 */
class GradeClient extends ResourceClient {
  constructor() {
    super('http://localhost:8000', 'grades')
    this.cacheTimeout = 10 * 60 * 1000 // 10分钟缓存
  }

  /**
   * 获取学期列表
   * @returns {Promise<Array>} 学期列表
   */
  async getSemesters() {
    const cacheKey = 'grade_semesters'
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request('/grades/semesters', {
        method: 'GET'
      })
      
      const semesters = response.map(item => ({
        id: item.id || item.semester,
        semester: item.semester,
        name: DataProcessor.formatSemester(item.semester),
        startDate: item.start_date,
        endDate: item.end_date,
        isCurrent: item.is_current || false
      }))
      
      // 学期信息缓存时间较长
      this.setCache(cacheKey, semesters, 60 * 60 * 1000)
      
      return semesters
    } catch (error) {
      console.error('[GradeClient] 获取学期列表失败:', error)
      throw error
    }
  }

  /**
   * 获取指定学期的成绩
   * @param {string} semester 学期代码
   * @param {boolean} useCache 是否使用缓存
   * @returns {Promise<Array>} 成绩列表
   */
  async getGradesBySemester(semester, useCache = true) {
    const cacheKey = `grades_semester_${semester}`
    
    if (useCache) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        console.log('[GradeClient] 📦 使用缓存的成绩数据')
        return cached
      }
    }

    try {
      const response = await this.request('/grades', {
        method: 'GET',
        data: { semester }
      })
      
      const processedGrades = this.processGradeList(response)
      
      // 设置缓存
      this.setCache(cacheKey, processedGrades, this.cacheTimeout)
      
      return processedGrades
    } catch (error) {
      console.error('[GradeClient] 获取学期成绩失败:', error)
      throw error
    }
  }

  /**
   * 获取所有成绩
   * @param {boolean} useCache 是否使用缓存
   * @returns {Promise<Array>} 所有成绩列表
   */
  async getAllGrades(useCache = true) {
    const cacheKey = 'all_grades'
    
    if (useCache) {
      const cached = this.getCache(cacheKey)
      if (cached) {
        return cached
      }
    }

    try {
      const response = await this.request('/grades/all', {
        method: 'GET'
      })
      
      const processedGrades = this.processGradeList(response)
      
      this.setCache(cacheKey, processedGrades, this.cacheTimeout)
      
      return processedGrades
    } catch (error) {
      console.error('[GradeClient] 获取所有成绩失败:', error)
      throw error
    }
  }

  /**
   * 获取成绩统计信息
   * @param {string} semester 学期代码，可选
   * @returns {Promise<Object>} 统计信息
   */
  async getGradeStatistics(semester = null) {
    const cacheKey = semester ? `grade_stats_${semester}` : 'grade_stats_all'
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const params = semester ? { semester } : {}
      const response = await this.request('/grades/statistics', {
        method: 'GET',
        data: params
      })
      
      const processedStats = this.processStatistics(response)
      
      // 统计信息缓存时间较长
      this.setCache(cacheKey, processedStats, 30 * 60 * 1000)
      
      return processedStats
    } catch (error) {
      console.error('[GradeClient] 获取成绩统计失败:', error)
      // 返回默认统计
      return this.getDefaultStatistics()
    }
  }

  /**
   * 获取GPA信息
   * @param {string} semester 学期代码，可选
   * @returns {Promise<Object>} GPA信息
   */
  async getGPA(semester = null) {
    try {
      const params = semester ? { semester } : {}
      const response = await this.request('/grades/gpa', {
        method: 'GET',
        data: params
      })
      
      return {
        currentGPA: parseFloat(response.current_gpa || 0).toFixed(2),
        cumulativeGPA: parseFloat(response.cumulative_gpa || 0).toFixed(2),
        creditPoints: response.credit_points || 0,
        totalCredits: response.total_credits || 0,
        rank: response.rank || null,
        percentile: response.percentile || null
      }
    } catch (error) {
      console.error('[GradeClient] 获取GPA失败:', error)
      return {
        currentGPA: '0.00',
        cumulativeGPA: '0.00',
        creditPoints: 0,
        totalCredits: 0,
        rank: null,
        percentile: null
      }
    }
  }

  /**
   * 获取成绩趋势数据
   * @returns {Promise<Object>} 趋势数据
   */
  async getGradeTrends() {
    const cacheKey = 'grade_trends'
    
    const cached = this.getCache(cacheKey)
    if (cached) {
      return cached
    }

    try {
      const response = await this.request('/grades/trends', {
        method: 'GET'
      })
      
      const processedTrends = this.processTrends(response)
      
      // 趋势数据缓存时间较长
      this.setCache(cacheKey, processedTrends, 30 * 60 * 1000)
      
      return processedTrends
    } catch (error) {
      console.error('[GradeClient] 获取成绩趋势失败:', error)
      return {
        gpaHistory: [],
        semesterComparison: [],
        subjectTrends: {}
      }
    }
  }

  /**
   * 获取不及格科目
   * @param {string} semester 学期代码，可选
   * @returns {Promise<Array>} 不及格科目列表
   */
  async getFailedCourses(semester = null) {
    try {
      const params = semester ? { semester, status: 'failed' } : { status: 'failed' }
      const response = await this.request('/grades/failed', {
        method: 'GET',
        data: params
      })
      
      return this.processGradeList(response)
    } catch (error) {
      console.error('[GradeClient] 获取不及格科目失败:', error)
      return []
    }
  }

  /**
   * 处理成绩列表数据
   * @param {Array|Object} data 原始数据
   * @returns {Array} 处理后的成绩列表
   */
  processGradeList(data) {
    let grades = []
    
    if (Array.isArray(data)) {
      grades = data
    } else if (data && data.list) {
      grades = data.list
    } else if (data && data.grades) {
      grades = data.grades
    } else {
      return []
    }

    return grades.map(item => this.processGradeItem(item))
  }

  /**
   * 处理单个成绩数据
   * @param {Object} item 原始成绩数据
   * @returns {Object} 处理后的成绩数据
   */
  processGradeItem(item) {
    if (!item || typeof item !== 'object') {
      return item
    }

    const score = parseFloat(item.score || item.final_score || 0)
    const credit = parseFloat(item.credit || item.credits || 0)

    return {
      id: item.id,
      courseId: item.course_id,
      courseName: item.course_name || item.name,
      courseCode: item.course_code || item.code,
      semester: item.semester,
      semesterName: DataProcessor.formatSemester(item.semester),
      credit: credit,
      score: score,
      scoreText: this.formatScore(score),
      gradeLevel: DataProcessor.formatGradeLevel(score),
      gradePoint: this.calculateGradePoint(score),
      status: this.getGradeStatus(score),
      isPassed: score >= 60,
      isFailed: score < 60 && score > 0,
      
      // 详细分数
      regularScore: parseFloat(item.regular_score || 0),
      midtermScore: parseFloat(item.midterm_score || 0),
      finalScore: parseFloat(item.final_score || score),
      
      // 其他信息
      teacher: item.teacher || '未知',
      examDate: item.exam_date ? DataProcessor.formatDate(item.exam_date) : null,
      examType: item.exam_type || 'written',
      courseType: item.course_type || 'required',
      department: item.department || '',
      
      // 原始数据
      raw: item
    }
  }

  /**
   * 处理统计数据
   * @param {Object} data 原始统计数据
   * @returns {Object} 处理后的统计数据
   */
  processStatistics(data) {
    return {
      totalCourses: data.total_courses || 0,
      passedCourses: data.passed_courses || 0,
      failedCourses: data.failed_courses || 0,
      totalCredits: data.total_credits || 0,
      earnedCredits: data.earned_credits || 0,
      averageScore: parseFloat(data.average_score || 0).toFixed(1),
      highestScore: data.highest_score || 0,
      lowestScore: data.lowest_score || 0,
      passRate: data.pass_rate ? `${(data.pass_rate * 100).toFixed(1)}%` : '0%',
      
      // 等级分布
      gradeDistribution: {
        A: data.grade_a || 0,
        B: data.grade_b || 0,
        C: data.grade_c || 0,
        D: data.grade_d || 0,
        F: data.grade_f || 0
      },
      
      // 科目类型统计
      courseTypeStats: {
        required: data.required_courses || 0,
        elective: data.elective_courses || 0,
        public: data.public_courses || 0
      }
    }
  }

  /**
   * 处理趋势数据
   * @param {Object} data 原始趋势数据
   * @returns {Object} 处理后的趋势数据
   */
  processTrends(data) {
    return {
      gpaHistory: (data.gpa_history || []).map(item => ({
        semester: item.semester,
        semesterName: DataProcessor.formatSemester(item.semester),
        gpa: parseFloat(item.gpa || 0).toFixed(2),
        credits: item.credits || 0
      })),
      
      semesterComparison: (data.semester_comparison || []).map(item => ({
        semester: item.semester,
        semesterName: DataProcessor.formatSemester(item.semester),
        averageScore: parseFloat(item.average_score || 0).toFixed(1),
        passRate: item.pass_rate ? `${(item.pass_rate * 100).toFixed(1)}%` : '0%',
        courseCount: item.course_count || 0
      })),
      
      subjectTrends: data.subject_trends || {}
    }
  }

  /**
   * 格式化分数显示
   * @param {number} score 分数
   * @returns {string} 格式化后的分数
   */
  formatScore(score) {
    if (score === null || score === undefined || score === 0) {
      return '未出分'
    }
    
    if (score < 0) {
      return '缺考'
    }
    
    return score.toString()
  }

  /**
   * 计算绩点
   * @param {number} score 分数
   * @returns {number} 绩点
   */
  calculateGradePoint(score) {
    if (score >= 90) return 4.0
    if (score >= 85) return 3.7
    if (score >= 82) return 3.3
    if (score >= 78) return 3.0
    if (score >= 75) return 2.7
    if (score >= 72) return 2.3
    if (score >= 68) return 2.0
    if (score >= 64) return 1.5
    if (score >= 60) return 1.0
    return 0.0
  }

  /**
   * 获取成绩状态
   * @param {number} score 分数
   * @returns {string} 状态
   */
  getGradeStatus(score) {
    if (score === null || score === undefined || score === 0) {
      return 'pending'
    }
    
    if (score < 0) {
      return 'absent'
    }
    
    if (score >= 60) {
      return 'passed'
    }
    
    return 'failed'
  }

  /**
   * 获取默认统计信息
   * @returns {Object} 默认统计
   */
  getDefaultStatistics() {
    return {
      totalCourses: 0,
      passedCourses: 0,
      failedCourses: 0,
      totalCredits: 0,
      earnedCredits: 0,
      averageScore: '0.0',
      highestScore: 0,
      lowestScore: 0,
      passRate: '0%',
      gradeDistribution: { A: 0, B: 0, C: 0, D: 0, F: 0 },
      courseTypeStats: { required: 0, elective: 0, public: 0 }
    }
  }

  /**
   * 错误处理
   * @param {Error} error 错误对象
   * @param {string} url 请求URL
   */
  handleError(error, url) {
    console.error(`[GradeClient] ❌ 请求失败:`, url, error.message)
    
    if (error.message.includes('401')) {
      throw new Error('登录已过期，请重新登录后查看成绩')
    } else if (error.message.includes('403')) {
      throw new Error('暂无权限查看成绩信息')
    } else if (error.message.includes('网络')) {
      throw new Error('网络连接失败，请检查网络设置')
    } else {
      throw error
    }
  }
}

module.exports = GradeClient 