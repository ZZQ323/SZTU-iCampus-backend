const { BasePage, createPage } = require('../../utils/BasePage') 

/**
 * 公告页面类 - 重构版本
 * 功能与原页面完全一致
 */
class AnnouncementsPage extends BasePage {
  
  getPageName() {
    return '公告页面'
  }

  getInitialData() {
    return {
      announcements: [],
      loading: false
    }
  }

  requiresLogin() {
    return false
  }

  async loadInitialData(options) {
    console.log('📱 公告页面加载 - 重构版本')
    await this.loadAnnouncements()
  }

  async refreshData(force = false) {
    await this.loadAnnouncements()
  }

  async loadAnnouncements() {
    try {
      this.setData({ loading: true })

      // 调用API获取公告
      const API = require('../../utils/api')
      const response = await API.getAnnouncements({
        page: 1,
        size: 10
      })
      
      console.log('✅ 公告数据:', response)
      
      if (response && response.code === 0) {
        const announcements = response.data?.items || []
        this.setData({ announcements })
        console.log(`📋 加载了 ${announcements.length} 条公告`)
      }
      
    } catch (error) {
      console.error('❌ 加载公告失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    } finally {
      this.setData({ loading: false })
    }
  }

  onPullDownRefresh() {
    this.loadAnnouncements().finally(() => {
      wx.stopPullDownRefresh()
    })
  }
}

// 创建页面实例并导出
const announcementsPage = new AnnouncementsPage()
module.exports = createPage(announcementsPage) 
