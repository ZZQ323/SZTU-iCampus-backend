/**
 * API 调用工具类
 * 统一管理所有的后端API请求，替换模拟数据
 */

const BASE_URL = 'http://127.0.0.1:8000/api/v1';

class API {
  /**
   * 通用请求方法
   */
  static async request(url, options = {}) {
    const token = wx.getStorageSync('token');
    
    console.log('🔍 [API调试] 当前存储的token:', token ? token.substring(0, 20) + '...' : 'null');
    
    const defaultOptions = {
      header: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    };

    const finalOptions = { ...defaultOptions, ...options };
    
    console.log('🔍 [API调试] 完整请求头:', finalOptions.header);
    
    try {
      console.log(`🔗 API请求: ${finalOptions.method || 'GET'} ${BASE_URL}${url}`);
      
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${BASE_URL}${url}`,
          ...finalOptions,
          success: resolve,
          fail: (error) => {
            console.error('❌ 网络请求失败:', error);
            // 提供更详细的错误信息
            if (error.errMsg && error.errMsg.includes('timeout')) {
              reject(new Error('请求超时，请检查网络连接或稍后重试'));
            } else if (error.errMsg && error.errMsg.includes('fail')) {
              reject(new Error('网络连接失败，请检查服务器状态'));
            } else {
              reject(error);
            }
          }
        });
      });

      console.log(`✅ API响应状态:`, response.statusCode);
      console.log(`✅ API响应数据:`, response.data);

      if (response.statusCode === 200) {
        // 🔧 返回完整的响应对象，让调用方决定如何处理
        return response.data;
      } else if (response.statusCode === 401) {
        // 处理认证失败
        console.warn('⚠️ 认证失败，清除token');
        wx.removeStorageSync('token');
        throw new Error('登录已过期，请重新登录');
      } else if (response.statusCode === 403) {
        throw new Error('权限不足');
      } else if (response.statusCode === 404) {
        throw new Error('请求的资源不存在');
      } else if (response.statusCode >= 500) {
        throw new Error('服务器内部错误，请稍后重试');
      } else {
        console.error('❌ API响应错误:', {
          statusCode: response.statusCode,
          response: response.data
        });
        throw new Error(response.data?.message || `请求失败(${response.statusCode})`);
      }
    } catch (error) {
      console.error(`❌ API错误:`, error);
      // 确保总是抛出Error对象
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error(error.message || '未知错误');
      }
    }
  }

  /**
   * GET 请求
   */
  static get(url, params = {}) {
    // 🔧 过滤掉 null、undefined 和空字符串参数
    const filteredParams = Object.keys(params)
      .filter(key => params[key] !== null && params[key] !== undefined && params[key] !== '')
      .reduce((obj, key) => {
        obj[key] = params[key];
        return obj;
      }, {});
    
    const queryString = Object.keys(filteredParams)
      .map(key => `${key}=${encodeURIComponent(filteredParams[key])}`)
      .join('&');
    
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    console.log('🔍 [API调试] 请求URL:', `${BASE_URL}${fullUrl}`);
    
    return this.request(fullUrl, { method: 'GET' });
  }

  /**
   * POST 请求
   */
  static post(url, data = {}) {
    return this.request(url, {
      method: 'POST',
      data: JSON.stringify(data)
    });
  }

  /**
   * PUT 请求
   */
  static put(url, data = {}) {
    return this.request(url, {
      method: 'PUT',
      data: JSON.stringify(data)
    });
  }

  /**
   * DELETE 请求
   */
  static delete(url) {
    return this.request(url, { method: 'DELETE' });
  }

  // ============ 用户相关 API ============
  
  /**
   * 获取当前用户信息
   */
  static getUserInfo() {
    return this.get('/users/me');
  }

  /**
   * 获取用户权限
   */
  static getUserPermissions() {
    return this.get('/users/me/permissions');
  }

  // ============ 课表相关 API ============
  
  /**
   * 获取课程表列表
   */
  static getSchedule(params = {}) {
    return this.get('/schedule', params);
  }

  /**
   * 获取当前周课程表
   */
  static getCurrentWeekSchedule() {
    return this.get('/schedule/current-week');
  }

  /**
   * 获取指定周课程表
   */
  static getWeekSchedule(weekNumber, semester) {
    return this.get(`/schedule/week/${weekNumber}`, { semester });
  }

  /**
   * 获取课程表网格数据
   */
  static getScheduleGrid(weekNumber) {
    return this.get(`/schedule/grid/${weekNumber}`);
  }

  // ============ 成绩相关 API ============
  
  /**
   * 获取成绩列表
   */
  static getGrades(params = {}) {
    return this.get('/grades', params);
  }

  /**
   * 获取指定学期成绩
   */
  static getSemesterGrades(semester) {
    return this.get(`/grades/semester/${semester}`);
  }

  /**
   * 获取成绩统计
   */
  static getGradeStatistics() {
    return this.get('/grades/statistics');
  }

  /**
   * 获取班级排名
   */
  static getGradeRanking() {
    return this.get('/grades/ranking');
  }

  /**
   * 获取可用学期列表
   */
  static getAvailableSemesters() {
    return this.get('/grades/semesters');
  }

  // ============ 考试相关 API ============
  
  /**
   * 获取考试列表
   */
  static getExams(params = {}) {
    return this.get('/exams', params);
  }

  /**
   * 获取考试详情
   */
  static getExamDetail(examId) {
    return this.get(`/exams/${examId}`);
  }

  /**
   * 获取考试倒计时
   */
  static getExamCountdown(examId) {
    return this.get(`/exams/${examId}/countdown`);
  }

  /**
   * 获取考试统计
   */
  static getExamStatistics() {
    return this.get('/exams/statistics');
  }

  /**
   * 获取成绩预告通知
   */
  static getGradeNotifications() {
    return this.get('/grades/notifications');
  }

  // ============ 图书馆相关 API ============
  
  /**
   * 图书搜索
   */
  static searchBooks(params = {}) {
    return this.get('/library/books/search', params);
  }

  /**
   * 获取借阅记录
   */
  static getBorrowRecords(params = {}) {
    return this.get('/library/borrows', params);
  }

  /**
   * 借阅图书
   */
  static borrowBook(bookId) {
    return this.post(`/library/borrows/${bookId}`);
  }

  /**
   * 续借图书
   */
  static renewBook(recordId) {
    return this.put(`/library/borrows/${recordId}/renew`);
  }

  /**
   * 获取座位信息
   */
  static getSeats() {
    return this.get('/library/seats');
  }

  /**
   * 获取座位信息（别名，兼容性）
   */
  static getSeatInfo() {
    return this.getSeats();
  }

  /**
   * 预约座位
   */
  static reserveSeat(areaId, durationHours = 4) {
    return this.post('/library/seats/reserve', { area_id: areaId, duration_hours: durationHours });
  }

  // ============ 校园卡相关 API ============
  
  /**
   * 获取校园卡信息
   */
  static getCampusCardInfo() {
    return this.get('/campus-card/info');
  }

  /**
   * 获取消费记录
   */
  static getTransactions(params = {}) {
    return this.get('/campus-card/transactions', params);
  }

  /**
   * 获取余额信息
   */
  static getBalance() {
    return this.get('/campus-card/balance');
  }

  /**
   * 获取消费统计
   */
  static getCampusCardStatistics(period = 'month') {
    return this.get('/campus-card/statistics', { period });
  }

  /**
   * 获取商户列表
   */
  static getMerchants() {
    return this.get('/campus-card/merchants');
  }

  // ============ 公告相关 API ============
  
  /**
   * 获取公告列表
   */
  static getAnnouncements(params = {}) {
    return this.get('/announcements', params);
  }

  /**
   * 获取公告详情
   */
  static getAnnouncementDetail(announcementId) {
    return this.get(`/announcements/${announcementId}`);
  }

  /**
   * 标记公告已读
   */
  static markAnnouncementRead(announcementId) {
    return this.post(`/announcements/${announcementId}/read`);
  }

  /**
   * 获取公告分类列表
   */
  static getAnnouncementCategories() {
    return this.get('/announcements/categories/list');
  }

  /**
   * 获取部门列表
   */
  static getAnnouncementDepartments() {
    return this.get('/announcements/departments/list');
  }

  /**
   * 获取紧急公告
   */
  static getUrgentAnnouncements(limit = 10) {
    return this.get('/announcements/urgent/list', { limit });
  }

  // ============ 活动相关 API ============
  
  /**
   * 获取活动列表
   */
  static getEvents(params = {}) {
    return this.get('/events', params);
  }

  /**
   * 获取活动详情
   */
  static getEventDetail(eventId) {
    return this.get(`/events/${eventId}`);
  }

  /**
   * 报名活动
   */
  static registerEvent(eventId) {
    return this.post(`/events/${eventId}/register`);
  }

  /**
   * 取消报名
   */
  static cancelEventRegistration(eventId) {
    return this.delete(`/events/${eventId}/register`);
  }

  // ============ 基础数据相关 API ============
  
  /**
   * 获取学院列表
   */
  static getColleges() {
    return this.get('/base/colleges');
  }

  /**
   * 获取专业列表
   */
  static getMajors(params = {}) {
    return this.get('/base/majors', params);
  }

  /**
   * 获取班级列表
   */
  static getClasses(params = {}) {
    return this.get('/base/classes', params);
  }

  /**
   * 获取部门列表
   */
  static getDepartments() {
    return this.get('/base/departments');
  }

  /**
   * 获取场所列表
   */
  static getLocations(params = {}) {
    return this.get('/base/locations', params);
  }

  // ============ 阅读记录相关 API ============
  
  /**
   * 记录阅读行为
   */
  static recordReading(contentType, contentId, readDuration = 0) {
    return this.post('/reading/record', {
      content_type: contentType,
      content_id: contentId,
      read_duration: readDuration
    });
  }

  /**
   * 获取阅读历史
   */
  static getReadingHistory(params = {}) {
    return this.get('/reading/history', params);
  }

  /**
   * 添加书签
   */
  static addBookmark(contentType, contentId, contentTitle) {
    return this.post('/reading/bookmark', {
      content_type: contentType,
      content_id: contentId,
      content_title: contentTitle
    });
  }

  /**
   * 获取书签列表
   */
  static getBookmarks(params = {}) {
    return this.get('/reading/bookmarks', params);
  }

  /**
   * 分享内容
   */
  static shareContent(contentType, contentId, shareMethod = 'link') {
    return this.post('/reading/share', {
      content_type: contentType,
      content_id: contentId,
      share_method: shareMethod
    });
  }

  /**
   * 获取阅读分析
   */
  static getReadingAnalytics(period = 'week') {
    return this.get('/reading/analytics', { period });
  }

  // ============ 管理员相关 API ============
  
  /**
   * 获取系统统计
   */
  static getAdminStats() {
    return this.get('/admin/stats');
  }

  /**
   * 获取用户列表
   */
  static getAdminUsers() {
    return this.get('/admin/users');
  }

  /**
   * 获取系统健康检查
   */
  static getSystemHealth() {
    return this.get('/admin/system-health');
  }

  /**
   * 获取系统日志
   */
  static getSystemLogs() {
    return this.get('/admin/logs');
  }
}

module.exports = API; 