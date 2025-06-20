// SZTU-iCampus 首页逻辑
Page({
  data: {
    homeData: {
      user_info: {
        name: "张三",
        student_id: "20241001001",
        avatar: "/assets/test/man.png",
        college: "计算机学院",
        unread_count: 3
      },
      quick_actions: [
        {name: "课表查询", icon: "schedule", path: "/pages/schedule/schedule"},
        {name: "成绩查询", icon: "Grade", path: "/pages/grades/grades"},
        {name: "图书馆", icon: "Library", path: "/pages/library/library"},
        {name: "校园卡", icon: "wallet", path: "/pages/campus-card/campus-card"},
        {name: "考试安排", icon: "examination", path: "/pages/exams/exams"},
        {name: "活动报名", icon: "event", path: "/pages/events/events"},
        {name: "通讯录", icon: "message", path: "/pages/address_book/address_book"},
        {name: "通知中心", icon: "notification", path: "/pages/announcements/announcements"}
      ],
      today_schedule: [
        {
          id: 1,
          course_name: "数据结构与算法",
          teacher: "李教授",
          time: "08:30-10:10",
          location: "C2-301",
          status: "upcoming"
        },
        {
          id: 2,
          course_name: "软件工程",
          teacher: "王教授",
          time: "10:30-12:10",
          location: "C2-305",
          status: "current"
        },
        {
          id: 3,
          course_name: "数据库原理",
          teacher: "张教授",
          time: "14:30-16:10",
          location: "C2-302",
          status: "upcoming"
        }
      ],
      announcements: [
        {
          id: 1,
          title: "关于2024年寒假放假安排的通知",
          department: "教务处",
          date: "2024-12-18",
          urgent: true,
          category: "教学"
        },
        {
          id: 2,
          title: "深圳技术大学第十二届运动会开幕式通知",
          department: "体育部",
          date: "2024-12-17",
          urgent: false,
          category: "活动"
        },
        {
          id: 3,
          title: "图书馆系统维护通知",
          department: "图书馆",
          date: "2024-12-16",
          urgent: false,
          category: "服务"
        }
      ],
      today_stats: {
        courses: 4,
        completed_courses: 1,
        library_books: 2,
        announcements: 5
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
    console.log('当前快捷功能数据:', this.data.homeData.quick_actions);
    this.loadHomeData();
  },

  /**
   * 页面显示时
   */
  onShow() {
    // 每次显示时刷新数据
    this.refreshData();
    this.checkQuickActions();
  },

  /**
   * 检查快捷功能数据
   */
  checkQuickActions() {
    console.log('=== 快捷功能数据检查 ===');
    const quickActions = this.data.homeData.quick_actions;
    console.log('快捷功能数组:', quickActions);
    console.log('数组长度:', quickActions ? quickActions.length : 0);
    
    if (quickActions && quickActions.length > 0) {
      quickActions.forEach((item, index) => {
        console.log(`第${index + 1}个功能:`, {
          name: item.name,
          icon: item.icon,
          path: item.path
        });
      });
    } else {
      console.error('快捷功能数据为空或未定义');
    }
    console.log('=== 检查结束 ===');
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.loadHomeData().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  /**
   * 加载首页数据
   */
  async loadHomeData() {
    try {
      this.setData({ loading: true });
      
      // 这里应该调用后端API获取数据
      // const res = await wx.request({
      //   url: 'http://localhost:8000/api/v1/simple/home',
      //   method: 'GET',
      //   header: {
      //     'Authorization': 'Bearer ' + wx.getStorageSync('token')
      //   }
      // });
      // 
      // if (res.data.success) {
      //   this.setData({
      //     homeData: res.data.data
      //   });
      // }

      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 500));
      
      console.log('首页数据加载完成');
    } catch (error) {
      console.error('加载首页数据失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  /**
   * 刷新数据
   */
  async refreshData() {
    // 静默刷新，不显示loading
    try {
      // 这里可以调用API获取最新数据
      console.log('静默刷新数据');
    } catch (error) {
      console.error('刷新数据失败:', error);
    }
  },

  /**
   * 通用页面跳转
   */
  navigateTo(e) {
    console.log('点击快捷按钮，事件对象:', e);
    const url = e.currentTarget.dataset.url;
    console.log('获取到的URL:', url);
    
    if (url) {
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
      console.error('URL为空，无法跳转');
      wx.showToast({
        title: '页面地址错误',
        icon: 'none'
      });
    }
  },

  /**
   * 跳转到公告详情
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
    wx.navigateTo({
      url: '/pages/notifications/notifications',
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
   * 页面相关事件处理函数--监听用户滑动
   */
  onPageScroll(e) {
    // 可以在这里处理滚动事件，比如改变导航栏样式
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
    // 可以在这里添加跳转到公告详情页面的逻辑
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