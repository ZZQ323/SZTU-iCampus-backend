const app = getApp()
const { EventStream, streamManager } = require('../../utils/stream')

Page({
  data: {
    currentYear: 2024,
    currentMonth: 1,
    calendarVisible: false,
    events: [],
    loading: true,
    error: '',
    eventTypes: ['全部', '学术活动', '社团活动', '体育活动', '文化活动', '比赛活动'],
    selectedType: '全部',
    eventStatuses: ['全部', '即将开始', '进行中', '已结束'],
    selectedStatus: '全部',
    organizers: ['全部', '学术委员会', '学生会', '体育部', '计算机学院', '社团联合会', '教务处'],
    isStreamConnected: false,  // 流式连接状态
    participantUpdates: 0      // 参与人数更新次数统计
  },

  onLoad() {
    this.setCurrentDate();
    this.loadEvents();
    // 🔥 启动流式活动数据推送 - 实时更新参与人数
    this.startEventStream();
  },

  setCurrentDate() {
    const now = new Date();
    this.setData({
      currentYear: now.getFullYear(),
      currentMonth: now.getMonth() + 1
    });
  },

  onBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  loadEvents() {
    this.setData({ loading: true, error: '' });
    
    // 构建请求参数
    let url = `${app.globalData.baseUrl}/api/events?limit=50`;
    
    if (this.data.selectedType !== '全部') {
      const typeMap = {
        '学术活动': 'academic',
        '社团活动': 'social',
        '体育活动': 'sports',
        '文化活动': 'cultural',
        '比赛活动': 'competition'
      };
      url += `&event_type=${typeMap[this.data.selectedType]}`;
    }
    
    if (this.data.selectedStatus !== '全部') {
      const statusMap = {
        '即将开始': 'upcoming',
        '进行中': 'ongoing',
        '已结束': 'completed'
      };
      url += `&status=${statusMap[this.data.selectedStatus]}`;
    }

    wx.request({
      url: url,
      method: 'GET',
      success: (res) => {
        console.log('活动API响应:', res.data);
        if (res.statusCode === 200 && res.data.code === 0) {
          // 处理活动数据，计算参与度百分比
          const events = (res.data.data.events || []).map(event => {
            if (event.max_participants && event.current_participants >= 0) {
              event.participationPercent = Math.min(Math.round((event.current_participants / event.max_participants) * 100), 100);
            } else {
              event.participationPercent = 0;
            }
            return event;
          });
          
          this.setData({
            events: events,
            loading: false
          });
        } else {
          console.error('获取活动失败:', res.data);
          this.setData({
            error: '获取活动失败，请稍后重试',
            loading: false
          });
        }
      },
      fail: (err) => {
        console.error('请求活动失败:', err);
        this.setData({
          error: '网络请求失败，请检查网络连接',
          loading: false
        });
      }
    });
  },

  // 🚀 启动流式活动数据推送 - 实时更新参与人数
  startEventStream() {
    const eventStream = new EventStream()
    
    console.log('[活动页面] 启动流式活动数据推送...')
    
    eventStream.start((updatedEvent) => {
      console.log('[活动页面] 收到活动数据更新:', updatedEvent)
      
      // 查找并更新对应的活动数据
      const events = this.data.events.map(event => {
        if (event.id === updatedEvent.id) {
          // 🎯 实时更新参与人数
          const updatedEventData = {
            ...event,
            current_participants: updatedEvent.current_participants,
            max_participants: updatedEvent.max_participants || event.max_participants
          }
          
          // 重新计算参与度百分比
          if (updatedEventData.max_participants && updatedEventData.current_participants >= 0) {
            updatedEventData.participationPercent = Math.min(
              Math.round((updatedEventData.current_participants / updatedEventData.max_participants) * 100), 
              100
            )
          }
          
          console.log(`[活动更新] ${event.title} 参与人数: ${event.current_participants} → ${updatedEvent.current_participants}`)
          
          return updatedEventData
        }
        return event
      })
      
      this.setData({
        events: events,
        participantUpdates: this.data.participantUpdates + 1
      })
      
      // 显示更新提醒（不要太频繁）
      if (this.data.participantUpdates % 3 === 0) {
        wx.showToast({
          title: '活动数据已更新',
          icon: 'none',
          duration: 1500
        })
      }
    })
    
    this.setData({ isStreamConnected: true })
    this.eventStream = eventStream
  },

  // 停止流式推送
  stopEventStream() {
    if (this.eventStream) {
      this.eventStream.stop()
      this.setData({ isStreamConnected: false })
      console.log('[活动页面] 停止流式活动数据推送')
    }
  },

  // 页面显示时重新连接流
  onShow() {
    if (!this.data.isStreamConnected) {
      this.startEventStream()
    }
  },

  // 页面隐藏时断开流（节省资源）
  onHide() {
    this.stopEventStream()
  },

  // 页面卸载时断开流
  onUnload() {
    this.stopEventStream()
  },

  onPullDownRefresh() {
    this.loadEvents();
    // 重置更新计数
    this.setData({ participantUpdates: 0 })
    setTimeout(() => {
      wx.stopPullDownRefresh();
    }, 1000);
  },

  onTypeChange(e) {
    const type = this.data.eventTypes[e.detail.value];
    this.setData({
      selectedType: type
    });
    this.loadEvents();
  },

  onStatusChange(e) {
    const status = this.data.eventStatuses[e.detail.value];
    this.setData({
      selectedStatus: status
    });
    this.loadEvents();
  },

  viewEvent(e) {
    const { id, title, description, organizer, location, start_time, end_time, requirements, contact_info } = e.currentTarget.dataset;
    
    // 显示活动详情
    wx.showModal({
      title: title,
      content: `${description}\n\n📅 时间：${start_time} - ${end_time}\n📍 地点：${location}\n👥 主办：${organizer}${requirements ? '\n\n📝 要求：' + requirements : ''}${contact_info ? '\n\n📞 联系：' + contact_info : ''}`,
      showCancel: true,
      cancelText: '关闭',
      confirmText: '我要参加',
      success: (res) => {
        if (res.confirm) {
          wx.showToast({
            title: '报名功能开发中',
            icon: 'none'
          });
        }
      }
    });
  },

  onDateSelect(e) {
    const { value } = e.detail;
    this.setData({
      calendarVisible: false
    });
    // TODO: 根据选择的日期筛选活动
    wx.showToast({
      title: '日期筛选开发中',
      icon: 'none'
    });
  },

  onCalendarClose() {
    this.setData({
      calendarVisible: false
    });
  },

  getEventTypeText(type) {
    const texts = {
      'academic': '学术',
      'social': '社团',
      'sports': '体育',
      'cultural': '文化',
      'competition': '比赛'
    };
    return texts[type] || '活动';
  },

  getStatusText(status) {
    const texts = {
      'upcoming': '即将开始',
      'ongoing': '进行中',
      'completed': '已结束',
      'cancelled': '已取消'
    };
    return texts[status] || '未知';
  },

  getStatusColor(status) {
    const colors = {
      'upcoming': '#007aff',
      'ongoing': '#34c759',
      'completed': '#8e8e93',
      'cancelled': '#ff3b30'
    };
    return colors[status] || '#8e8e93';
  }
}); 