/**
 * SZTU-iCampus 前端测试配置
 * 包含固定的测试用户和推送事件配置
 */

const FRONTEND_TEST_CONFIG = {
  // API配置
  api: {
    baseUrl: 'http://localhost:8000/api/v1',
    streamEndpoints: {
      events: '/stream/events',
      sync: '/stream/sync',
      status: '/stream/status'
    }
  },

  // 固定测试用户 (所有密码: 123456)
  testUsers: {
    // 学生用户 - 可接收: 成绩、消费、图书、课程变更
    students: [
      { loginId: '202100000001', name: '唐勇', password: '123456' },
      { loginId: '202100000002', name: '郭文', password: '123456' },
      { loginId: '202100000003', name: '周平', password: '123456' },
      { loginId: '202100000004', name: '黄强', password: '123456' },
      { loginId: '202100000005', name: '徐丽', password: '123456' }
    ],

    // 教师用户 - 可接收: 课程变更、系统消息
    teachers: [
      { loginId: '2025001001', name: '高军', password: '123456' },
      { loginId: '2025001002', name: '陈建华', password: '123456' }
    ],

    // 管理员用户 - 可接收: 所有事件
    admins: [
      { loginId: '2025000001', name: '何平', password: '123456' }
    ],

    // 获取推荐的测试用户
    getRecommended() {
      return {
        student: this.students[0],    // 唐勇
        teacher: this.teachers[0],    // 高军
        admin: this.admins[0]         // 何平
      };
    },

    // 根据用户类型获取用户列表
    getByType(userType) {
      switch (userType) {
        case 'student': return this.students;
        case 'teacher': return this.teachers;
        case 'admin': return this.admins;
        default: return [...this.students, ...this.teachers, ...this.admins];
      }
    }
  },

  // 事件类型配置
  eventTypes: {
    // 公开事件 (所有用户都能收到)
    public: [
      {
        type: 'announcement',
        name: '系统公告',
        icon: '📢',
        description: '校园重要通知，所有用户都能收到',
        targetUsers: 'all'
      }
    ],

    // 私人事件 (仅相关用户收到)
    private: [
      {
        type: 'grade_update',
        name: '成绩更新',
        icon: '📊',
        description: '课程成绩发布或更新',
        targetUsers: ['student']
      },
      {
        type: 'transaction',
        name: '消费流水',
        icon: '💳',
        description: '校园卡消费记录',
        targetUsers: ['student']
      },
      {
        type: 'library_reminder',
        name: '图书提醒',
        icon: '📚',
        description: '图书到期或续借提醒',
        targetUsers: ['student']
      },
      {
        type: 'course_change',
        name: '课程变更',
        icon: '📅',
        description: '课程时间或地点变更通知',
        targetUsers: ['student', 'teacher']
      }
    ],

    // 获取用户可接收的事件类型
    getEventsForUser(userType) {
      const publicEvents = this.public;
      const privateEvents = this.private.filter(event => 
        event.targetUsers.includes(userType) || event.targetUsers.includes('all')
      );
      return [...publicEvents, ...privateEvents];
    }
  },

  // 模拟推送数据
  mockPushData: {
    announcement: {
      title: '关于期末考试安排的重要通知',
      content: '各位同学，期末考试将于下周开始，请做好准备。考试时间安排请查看教务系统。',
      department: '教务处',
      urgent: true
    },

    grade_update: {
      course_name: '高等数学A',
      score: 90,
      grade_level: 'A-',
      semester: '2024-2025-1'
    },

    transaction: {
      amount: -15.50,
      location: '第一食堂',
      balance: 284.50,
      time: '12:30:15'
    },

    library_reminder: {
      book_title: '算法导论（第三版）',
      due_date: '2024-12-25',
      days_left: 4,
      fine_amount: 0.0
    },

    course_change: {
      course_name: '数据结构与算法',
      teacher: '李教授',
      old_schedule: '周一 08:30-10:10 @ C2-301',
      new_schedule: '周一 10:30-12:10 @ C2-305',
      reason: '教室设备维护',
      effective_date: '2024-12-25'
    }
  },

  // 测试辅助方法
  utils: {
    // 生成模拟登录请求
    generateLoginRequest(userType = 'student', index = 0) {
      const users = FRONTEND_TEST_CONFIG.testUsers.getByType(userType);
      const user = users[index] || users[0];
      
      return {
        url: `${FRONTEND_TEST_CONFIG.api.baseUrl}/auth/login`,
        method: 'POST',
        data: {
          username: user.loginId,
          password: user.password
        }
      };
    },

    // 生成事件订阅配置
    generateStreamConfig(token) {
      return {
        url: `${FRONTEND_TEST_CONFIG.api.baseUrl}${FRONTEND_TEST_CONFIG.api.streamEndpoints.events}`,
        headers: {
          'Authorization': `Bearer ${token}`
        }
      };
    },

    // 格式化事件显示
    formatEventForDisplay(event) {
      const eventConfig = [...FRONTEND_TEST_CONFIG.eventTypes.public, ...FRONTEND_TEST_CONFIG.eventTypes.private]
        .find(config => config.type === event.event_type);
      
      if (!eventConfig) return event;

      return {
        ...event,
        displayName: eventConfig.name,
        icon: eventConfig.icon,
        description: eventConfig.description
      };
    },

    // 获取事件通知文本
    getNotificationText(event) {
      switch (event.event_type) {
        case 'announcement':
          return `📢 ${event.data.title}`;
        case 'grade_update':
          return `📊 ${event.data.course_name}: ${event.data.score}分`;
        case 'transaction':
          return `💳 ${event.data.location} ${event.data.amount}元`;
        case 'library_reminder':
          return `📚 《${event.data.book_title}》还有${event.data.days_left}天到期`;
        case 'course_change':
          return `📅 ${event.data.course_name} 时间地点有变动`;
        default:
          return '新消息';
      }
    }
  }
};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
  // Node.js 环境
  module.exports = FRONTEND_TEST_CONFIG;
} else {
  // 浏览器环境
  window.FRONTEND_TEST_CONFIG = FRONTEND_TEST_CONFIG;
}

/**
 * 使用示例:
 * 
 * // 1. 获取推荐测试用户
 * const users = FRONTEND_TEST_CONFIG.testUsers.getRecommended();
 * console.log('学生:', users.student);
 * 
 * // 2. 生成登录请求
 * const loginReq = FRONTEND_TEST_CONFIG.utils.generateLoginRequest('student', 0);
 * 
 * // 3. 格式化事件显示
 * const formattedEvent = FRONTEND_TEST_CONFIG.utils.formatEventForDisplay(receivedEvent);
 * 
 * // 4. 获取通知文本
 * const notificationText = FRONTEND_TEST_CONFIG.utils.getNotificationText(receivedEvent);
 */ 