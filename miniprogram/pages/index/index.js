// SZTU-iCampus 首页逻辑
const app = getApp()
const API = require('../../utils/api')

Page({
  data: {
    userInfo: null,
    isLoggedIn: false,
    homeData: {
      user_info: {
        name: "未登录",
        student_id: "",
        avatar: "/assets/test/man.png",
        college: "",
        unread_count: 0
      },
      quick_actions: [],
      today_schedule: [],
      announcements: [],
      today_stats: {
        courses: 0,
        completed_courses: 0,
        library_books: 0,
        announcements: 0
      }
    },
    loading: false,
    showDialog: false,
    dialogData: {
      title: '',
      content: ''
    }
  },

  /**
   * 页面加载时
   */
  onLoad() {
    console.log('首页加载');
    this.checkLoginStatus();
  },

  /**
   * 页面显示时
   */
  onShow() {
    // 每次显示时检查登录状态并刷新数据
    this.checkLoginStatus();
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    // 为什么是通过token判断是否登录呢？
    // 但是好像我这个CORS配置并不影响；
    if (token && userInfo) {
      // 已登录
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo
      });
      console.log('用户已登录:', userInfo);
      this.loadUserHomeData(userInfo);
    } else {
      // 未登录
      this.setData({
        isLoggedIn: false,
        userInfo: null
      });
      console.log('用户未登录');
      this.loadGuestHomeData();
    }
  },

  /**
   * 加载已登录用户的首页数据
   */
  async loadUserHomeData(userInfo) {
    try {
      this.setData({ loading: true });
      // 根据用户类型设置快捷操作
      const quickActions = this.getQuickActionsByUserType(userInfo.person_type);
      // 设置用户信息
      const userData = {
        name: userInfo.name,
        student_id: userInfo.student_id || userInfo.employee_id || userInfo.login_id,
        avatar: "/assets/test/man.png",
        college: userInfo.college_name || '深圳技术大学',
        major: userInfo.major_name || '',
        class_name: userInfo.class_name || '',
        person_type: userInfo.person_type,
        unread_count: 0 // TODO: 从API获取
      };

      // 调用后端API获取用户相关数据
      const homeData = {
        user_info: userData,
        quick_actions: quickActions,
        today_schedule: await this.getTodaySchedule(userInfo),
        announcements: await this.getAnnouncements(userInfo),
        today_stats: await this.getTodayStats(userInfo)
      };

      this.setData({
        homeData: homeData
      });

      console.log('用户首页数据加载完成:', homeData);
    } catch (error) {
      console.error('加载用户首页数据失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  /**
   * 加载访客模式首页数据
   * 没登录展示默认数据，登录展示个人数据
   */
  loadGuestHomeData() {
    const guestData = {
      user_info: {
        name: "访客用户",
        student_id: "",
        avatar: "/assets/test/man.png",
        college: "深圳技术大学",
        unread_count: 0
      },
      quick_actions: [
        {name: "登录", icon: "home", action: "login"},
        {name: "校园地图", icon: "notification", path: "/pages/campus-map/campus-map"},
        {name: "联系我们", icon: "message", action: "contact"}
      ],
      today_schedule: [],
      announcements: [
        {
          id: 1,
          title: "欢迎使用SZTU iCampus",
          department: "系统",
          date: "2024-12-21",
          urgent: false,
          category: "系统"
        }
      ],
      today_stats: {
        courses: 0,
        completed_courses: 0,
        library_books: 0,
        announcements: 1
      }
    };

    this.setData({
      homeData: guestData
    });
  },

  /**
   * 根据用户类型获取快捷操作
   */
  getQuickActionsByUserType(personType) {
    const baseActions = [
      {name: "通知中心", icon: "notification", path: "/pages/announcements/announcements"},
      {name: "通讯录", icon: "message", path: "/pages/address_book/address_book"}
    ];

    switch (personType) {
      case 'student':
        return [
          {name: "课表查询", icon: "schedule", path: "/pages/schedule/schedule"},
          {name: "成绩查询", icon: "Grade", path: "/pages/grades/grades"},
          {name: "图书馆", icon: "Library", path: "/pages/library/library"},
          {name: "校园卡", icon: "wallet", path: "/pages/campus-card/campus-card"},
          {name: "考试安排", icon: "examination", path: "/pages/exams/exams"},
          {name: "活动报名", icon: "event", path: "/pages/events/events"},
          ...baseActions
        ];
      
      case 'teacher':
      case 'assistant_teacher':
        return [
          {name: "我的课程", icon: "schedule", path: "/pages/my-courses/my-courses"},
          {name: "成绩管理", icon: "Grade", path: "/pages/grade-management/grade-management"},
          {name: "学生管理", icon: "message", path: "/pages/student-management/student-management"},
          {name: "课程资料", icon: "Library", path: "/pages/course-materials/course-materials"},
          {name: "考试管理", icon: "examination", path: "/pages/exam-management/exam-management"},
          ...baseActions
        ];
      
      case 'admin':
        return [
          {name: "系统管理", icon: "home", path: "/pages/admin/admin"},
          {name: "用户管理", icon: "message", path: "/pages/user-management/user-management"},
          {name: "课程管理", icon: "schedule", path: "/pages/course-management/course-management"},
          {name: "成绩管理", icon: "Grade", path: "/pages/grade-management/grade-management"},
          {name: "数据统计", icon: "examination", path: "/pages/statistics/statistics"},
          {name: "系统设置", icon: "notification", path: "/pages/system-settings/system-settings"},
          ...baseActions
        ];
      
      case 'guest':
      default:
        return [
          {name: "登录", icon: "home", action: "login"},
          {name: "校园介绍", icon: "notification", path: "/pages/campus-intro/campus-intro"},
          {name: "联系我们", icon: "message", action: "contact"}
        ];
    }
  },

  /**
   * 获取今日课表（真实API）
   */
  async getTodaySchedule(userInfo) {
    try {
      if (userInfo.person_type === 'student') {
        // 🔧 增加错误处理，避免认证失败
        try {
          // 获取当前周课程表
          const scheduleData = await API.getCurrentWeekSchedule();
          
          // 获取今天是周几
          const today = new Date();
          const weekday = today.getDay() || 7; // 周日为0，转换为7
          
          // 🔧 修复：正确访问嵌套的data.courses
          const todayCourses = scheduleData.data?.courses || [];
          const todaySchedule = todayCourses
            .filter(course => course.weekday === weekday)
            .map(course => ({
              id: course.course_id,
              course_name: course.course_name,
              teacher: course.teacher_name,
              time: `${course.start_time}-${course.end_time}`,
              location: course.location,
              status: this.getCourseStatus(course.start_time, course.end_time)
            }))
            .slice(0, 3); // 最多显示3条
          
          return todaySchedule;
        } catch (apiError) {
          console.warn('API调用失败，返回空课表:', apiError);
          return [];
        }
      } else if (userInfo.person_type === 'teacher') {
        // 教师暂时返回空数组，后续可以实现教师课表
        return [];
      }
      return [];
    } catch (error) {
      console.error('获取今日课表失败:', error);
      return [];
    }
  },

  /**
   * 判断课程状态
   */
  getCourseStatus(startTime, endTime) {
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    
    const [startHour, startMin] = startTime.split(':').map(Number);
    const [endHour, endMin] = endTime.split(':').map(Number);
    
    const courseStart = startHour * 60 + startMin;
    const courseEnd = endHour * 60 + endMin;
    
    if (currentTime < courseStart) {
      return 'upcoming';
    } else if (currentTime >= courseStart && currentTime <= courseEnd) {
      return 'current';
    } else {
      return 'completed';
    }
  },

  /**
   * 获取公告信息（真实API）
   */
  async getAnnouncements(userInfo) {
    try {
      // 🔧 增加错误处理，避免认证失败
      try {
        // 获取最新的5条公告
        const announcementsData = await API.getAnnouncements({
          page: 1,
          size: 5,
          sort: 'publish_time',
          order: 'desc'
        });
        
        // 🔧 修复：正确访问嵌套的data.announcements
        const announcements = announcementsData.data?.announcements || [];
        
        return announcements.map(item => ({
          id: item.announcement_id,
          title: item.title,
          department: item.department,
          date: item.publish_time.split('T')[0], // 只取日期部分
          urgent: item.is_urgent || item.priority === 'high',
          category: item.category
        }));
      } catch (apiError) {
        console.warn('公告API调用失败，返回默认公告:', apiError);
        throw apiError;  // 重新抛出，让外层catch处理
      }
    } catch (error) {
      console.error('获取公告信息失败:', error);
      // 出错时返回默认公告
      return [
        {
          id: 'default_1',
          title: "欢迎使用SZTU iCampus",
          department: "系统",
          date: new Date().toISOString().split('T')[0],
          urgent: false,
          category: "系统"
        }
      ];
    }
  },

  /**
   * 获取今日统计（真实API）
   */
  async getTodayStats(userInfo) {
    try {
      if (userInfo.person_type === 'student') {
        // 学生统计数据 - 增加错误处理
        const results = await Promise.allSettled([
          API.getCurrentWeekSchedule().catch(() => ({ data: { courses: [] } })),
          API.getBorrowRecords({ status: 'borrowed' }).catch(() => ({ data: { borrow_records: [] } })),
          API.getAnnouncements({ page: 1, size: 1 }).catch(() => ({ data: { pagination: { total: 0 } } }))
        ]);

        // 计算今日课程数
        const today = new Date();
        const weekday = today.getDay() || 7;
        
        const scheduleResult = results[0];
        const borrowResult = results[1]; 
        const announcementResult = results[2];
        
        // 🔧 安全地访问数据
        const todayCourses = scheduleResult.status === 'fulfilled' 
          ? (scheduleResult.value.data?.courses || []).filter(course => course.weekday === weekday)
          : [];

        // 计算已完成课程数
        const completedCourses = todayCourses.filter(course => 
          this.getCourseStatus(course.start_time, course.end_time) === 'completed'
        ).length;

        return {
          courses: todayCourses.length,
          completed_courses: completedCourses,
          library_books: borrowResult.status === 'fulfilled' 
            ? (borrowResult.value.data?.borrow_records || []).length 
            : 0,
          announcements: announcementResult.status === 'fulfilled' 
            ? (announcementResult.value.data?.pagination?.total || 0)
            : 0
        };
      } else if (userInfo.person_type === 'teacher') {
        // 教师统计数据
        return {
          courses: 0, // 教师课程数量
          completed_courses: 0,
          students: 0, // 教师学生数量
          announcements: 0
        };
      } else if (userInfo.person_type === 'admin') {
        // 管理员统计数据
        try {
          const adminStatsData = await API.getAdminStats().catch(() => ({}));
          
          return {
            total_users: adminStatsData.total_users || 63460,
            active_sessions: adminStatsData.active_sessions || 0,
            system_alerts: adminStatsData.system_alerts || 0,
            announcements: adminStatsData.total_announcements || 0
          };
        } catch (error) {
          console.warn('管理员统计API失败:', error);
          return {
            total_users: 63460,
            active_sessions: 0,
            system_alerts: 0,
            announcements: 0
          };
        }
      }
      
      return {
        courses: 0,
        completed_courses: 0,
        library_books: 0,
        announcements: 0
      };
    } catch (error) {
      console.error('获取今日统计失败:', error);
      
      // 出错时返回默认值
      if (userInfo.person_type === 'student') {
        return {
          courses: 0,
          completed_courses: 0,
          library_books: 0,
          announcements: 0
        };
      } else if (userInfo.person_type === 'teacher') {
        return {
          courses: 0,
          completed_courses: 0,
          students: 0,
          announcements: 0
        };
      } else if (userInfo.person_type === 'admin') {
        return {
          total_users: 0,
          active_sessions: 0,
          system_alerts: 0,
          announcements: 0
        };
      }
      
      return {
        courses: 0,
        completed_courses: 0,
        library_books: 0,
        announcements: 0
      };
    }
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.checkLoginStatus();
    setTimeout(() => {
      wx.stopPullDownRefresh();
    }, 1000);
  },

  /**
   * 通用页面跳转和操作处理
   * 主要是配合快捷访问的
   */
  navigateTo(e) {
    console.log('点击快捷按钮，事件对象:', e);
    const url = e.currentTarget.dataset.url;
    const action = e.currentTarget.dataset.action;
    console.log('获取到的URL:', url, 'Action:', action);
    
    // 处理特殊操作
    if (action) {
      this.handleSpecialAction(action);
      return;
    }
    
    if (url) {
      // 检查是否需要登录
      if (!this.data.isLoggedIn && this.isProtectedPage(url)) {
        wx.showModal({
          title: '需要登录',
          content: '该功能需要登录后才能使用，是否前往登录？',
          success: (res) => {
            if (res.confirm) {
              this.goToLogin();
            }
          }
        });
        return;
      }

      // 定义 tabBar 页面列表
      const tabBarPages = [
        '/pages/index/index',
        '/pages/announcements/announcements', 
        '/pages/schedule/schedule',
        '/pages/address_book/address_book',
        '/pages/campus-card/campus-card'
      ];
      
      const isTabBarPage = tabBarPages.includes(url);
      console.log('是否为tabBar页面:', isTabBarPage);
      
      if (isTabBarPage) {
        // 跳转到 tabBar 页面
        console.log('使用switchTab跳转到:', url);
        wx.switchTab({
          url: url,
          success: (res) => {
            console.log('tabBar页面跳转成功:', res);
          },
          fail: (err) => {
            console.error('tabBar页面跳转失败:', err);
            wx.showToast({
              title: '页面跳转失败',
              icon: 'none'
            });
          }
        });
      } else {
        // 跳转到普通页面
        console.log('使用navigateTo跳转到:', url);
        wx.navigateTo({
          url: url,
          success: (res) => {
            console.log('普通页面跳转成功:', res);
          },
          fail: (err) => {
            console.error('普通页面跳转失败:', err);
            wx.showToast({
              title: '页面暂未开放',
              icon: 'none'
            });
          }
        });
      }
    } else {
      console.error('URL和Action都为空，无法执行操作');
      wx.showToast({
        title: '操作无效',
        icon: 'none'
      });
    }
  },

  /**
   * 处理特殊操作
   */
  handleSpecialAction(action) {
    switch (action) {
      case 'login':
        this.goToLogin();
        break;
      case 'contact':
        wx.showModal({
          title: '联系我们',
          content: '邮箱: support@sztu.edu.cn\n电话: 0755-23256054',
          showCancel: false
        });
        break;
      default:
        wx.showToast({
          title: '功能开发中',
          icon: 'none'
        });
    }
  },

  /**
   * 检查是否为需要登录才能查看的页面
   */
  isProtectedPage(url) {
    const protectedPages = [
      '/pages/schedule/schedule',
      '/pages/grades/grades',
      '/pages/campus-card/campus-card',
      '/pages/exams/exams',
      '/pages/library/library'
    ];
    return protectedPages.includes(url);
  },

  /**
   * 前往登录页面
   */
  goToLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    });
  },

  /**
   * 直接跳转到公告详情页
   */
  navigateToAnnouncement(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/announcement-detail/announcement-detail?id=${id}`,
      fail: (err) => {
        console.error('跳转公告详情失败:', err);
        wx.showToast({
          title: '页面暂未开放',
          icon: 'none'
        });
      }
    });
  },

  /**
   * 打开通知中心
   */
  openNotifications() {
    if (!this.data.isLoggedIn) {
      this.goToLogin();
      return;
    }
    
    wx.switchTab({
      url: '/pages/announcements/announcements',
      fail: (err) => {
        console.error('打开通知中心失败:', err);
        wx.showToast({
          title: '页面暂未开放',
          icon: 'none'
        });
      }
    });
  },

  /**
   * 用户头像点击 - 显示用户菜单
   */
  onUserAvatarTap() {
    if (!this.data.isLoggedIn) {
      this.goToLogin();
      return;
    }

    const userInfo = this.data.userInfo;
    const menuItems = ['个人资料', '账号设置', '退出登录'];
    
    wx.showActionSheet({
      itemList: menuItems,
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            // 个人资料
            wx.navigateTo({
              url: '/pages/profile/profile'
            });
            break;
          case 1:
            // 账号设置
            wx.navigateTo({
              url: '/pages/settings/settings'
            });
            break;
          case 2:
            // 退出登录
            this.logout();
            break;
        }
      }
    });
  },

  /**
   * 退出登录
   */
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除登录信息
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          app.globalData.userInfo = null;
          
          // 重新检查登录状态
          this.checkLoginStatus();
          
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
        }
      }
    });
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {
    console.log('首页渲染完成');
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {
    console.log('首页隐藏');
  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {
    console.log('首页卸载');
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: 'SZTU校园服务',
      path: '/pages/index/index',
      imageUrl: '/assets/icons/home.png'
    };
  },

  /**
   * 用户点击右上角分享到朋友圈
   */
  onShareTimeline() {
    return {
      title: 'SZTU校园服务 - 你的校园生活助手',
      imageUrl: '/assets/icons/home.png'
    };
  },

  /**
   * 对话框确认按钮
   */
  onDialogConfirm() {
    this.setData({
      showDialog: false
    });
  },

  /**
   * 对话框取消按钮
   */
  onDialogCancel() {
    this.setData({
      showDialog: false
    });
  }
}); 