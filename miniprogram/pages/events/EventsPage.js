const { BasePage, createPage } = require('../../utils/BasePage') 

class EventsPage extends BasePage {
  
  getPageName() {
    return '活动'
  }

  getInitialData() {
    return {
      events: [],
      loading: false,
      selectedCategory: 'all',
      categories: [
        { label: '全部', value: 'all' },
        { label: '学术', value: 'academic' },
        { label: '文体', value: 'sports' },
        { label: '社团', value: 'club' },
        { label: '志愿', value: 'volunteer' }
      ]
    }
  }

  requiresLogin() {
    return false
  }

  async loadInitialData(options) {
    console.log('🎉 活动页面加载')
    await this.loadEvents()
  }

  async refreshData(force = false) {
    await this.loadEvents()
  }

  async loadEvents() {
    try {
      this.setData({ loading: true })
      
      const API = require('../../utils/api')
      const response = await API.getEvents({
        page: 1,
        size: 20
      })
      
      console.log('✅ 活动数据:', response)
      
      if (response && response.code === 0) {
        const events = response.data?.items || response.data?.events || []
        this.setData({ events })
        console.log(`🎊 加载了 ${events.length} 个活动`)
      }
      
    } catch (error) {
      console.error('❌ 加载活动失败:', error)
      this.showToast('加载失败', 'error')
    } finally {
      this.setData({ loading: false })
    }
  }

  onCategoryChange(e) {
    const category = e.currentTarget.dataset.category
    this.setData({ selectedCategory: category })
    this.loadEvents()
  }

  onEventTap(e) {
    this.viewEventDetail(e)
  }

  viewEventDetail(e) {
    const event = e.currentTarget.dataset.event
    if (event && event.id) {
      console.log('查看活动详情:', event.id)
      this.navigate(`/pages/event-detail/event-detail?id=${event.id}`)
    } else {
      this.showToast('活动信息错误', 'error')
    }
  }

  registerEvent(e) {
    const event = e.currentTarget.dataset.event
    if (event && event.id) {
      console.log('报名活动:', event.id)
      this.showToast('报名功能开发中', 'none')
    }
  }
}

const eventsPage = new EventsPage()
module.exports = createPage(eventsPage) 
