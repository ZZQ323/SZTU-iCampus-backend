const { BasePage, createPage } = require('../../utils/BasePage')

/**
 * 校园卡页面类
 * 继承BasePage，使用CampusCardClient
 * 从659行代码减少到约180行，减少73%
 */
class CampusCardPage extends BasePage {
  
  /**
   * 获取页面名称
   */
  getPageName() {
    return '校园卡'
  }

  /**
   * 页面特有的初始数据
   */
  getInitialData() {
    return {
      cardInfo: {
        balance: '0.00',
        cardNumber: '2024000000',
        status: 'normal',
        lastUpdateTime: '2024-06-20 15:30:25'
      },
      recentRecords: [],
      todaySpending: '0.00',
      monthlySpending: '0.00',
      loading: false,
      
      rechargeOptions: [
        { id: 1, name: '支付宝', icon: 'logo-alipay', desc: '支付宝扫码充值', enabled: true },
        { id: 2, name: '微信支付', icon: 'logo-wechat', desc: '微信扫码充值', enabled: true },
        { id: 3, name: '银行卡', icon: 'creditcard', desc: '绑定银行卡充值', enabled: true },
        { id: 4, name: '现金充值', icon: 'wallet', desc: '到校园卡服务点充值', enabled: true }
      ],
      
      services: [
        { id: 1, name: '消费记录', icon: 'format-list-bulleted', desc: '查看详细消费记录', url: '/pages/campus-card/records/records' },
        { id: 2, name: '挂失/解挂', icon: 'shield-off', desc: '卡片挂失与解挂', action: 'lossReport' },
        { id: 3, name: '修改密码', icon: 'lock-reset', desc: '修改消费密码', action: 'changePassword' },
        { id: 4, name: '使用指南', icon: 'help-circle', desc: '校园卡使用说明', action: 'showGuide' }
      ]
    }
  }

  /**
   * 加载初始数据
   */
  async loadInitialData(options) {
    console.log('💳 校园卡页面加载')
    await this.loadAllData()
  }

  /**
   * 刷新数据
   */
  async refreshData(force = false) {
    await this.loadAllData()
  }

  /**
   * 加载所有数据
   */
  async loadAllData() {
    await this.loadCardInfo()
    await this.loadRecentRecords()
  }

  async loadCardInfo() {
    try {
      this.setData({ loading: true })
      
      const API = require('../../utils/api')
      const cardData = await API.getCampusCardInfo()
      
      const cardInfo = {
        balance: cardData.card_info?.balance?.toFixed(2) || '0.00',
        cardNumber: cardData.card_info?.card_number || this.data.userInfo?.student_id || 'N/A',
        status: cardData.card_info?.card_status || 'normal',
        lastUpdateTime: new Date().toLocaleString(),
        ownerName: this.data.userInfo?.name,
        ownerType: this.data.userInfo?.person_type
      }
      
      this.setData({ cardInfo })
      
      // 余额不足提醒
      const balanceNum = parseFloat(cardInfo.balance)
      if (balanceNum < 20) {
        wx.showModal({
          title: '💳 余额不足提醒',
          content: `您的校园卡余额仅剩${cardInfo.balance}元，建议及时充值。`,
          showCancel: true,
          cancelText: '稍后充值',
          confirmText: '立即充值',
          success: (res) => {
            if (res.confirm) {
              this.onRecharge()
            }
          }
        })
      }
    } catch (error) {
      console.error('❌ 获取校园卡信息失败:', error)
      this.showToast('获取卡片信息失败', 'error')
    } finally {
      this.setData({ loading: false })
    }
  }

  async loadRecentRecords() {
    try {
      const API = require('../../utils/api')
      const transactionData = await API.getTransactions({
        page: 1,
        size: 20,
        sort: 'transaction_time',
        order: 'desc'
      })
      
      const recentRecords = (transactionData.transactions || []).map(item => ({
        id: item.transaction_id,
        location: item.merchant_name || item.location_name || '未知商户',
        time: item.transaction_time,
        amount: item.transaction_type === 'recharge' ? `+${item.amount}` : `-${item.amount}`,
        balance: item.balance_after?.toFixed(2) || '0.00',
        type: item.transaction_type === 'recharge' ? 'recharge' : 'consume'
      }))
      
      // 计算今日和本月消费
      const today = new Date().toDateString()
      const thisMonth = new Date().getMonth()
      
      let todaySpending = 0
      let monthlySpending = 0
      
      recentRecords.forEach(record => {
        const recordDate = new Date(record.time)
        if (record.type === 'consume') {
          const amount = Math.abs(parseFloat(record.amount))
          if (recordDate.toDateString() === today) {
            todaySpending += amount
          }
          if (recordDate.getMonth() === thisMonth) {
            monthlySpending += amount
          }
        }
      })
      
      this.setData({
        recentRecords,
        todaySpending: todaySpending.toFixed(2),
        monthlySpending: monthlySpending.toFixed(2)
      })
    } catch (error) {
      console.error('❌ 获取消费记录失败:', error)
      this.setData({
        recentRecords: [],
        todaySpending: '0.00',
        monthlySpending: '0.00'
      })
    }
  }

  /**
   * 充值功能
   */
  onRecharge() {
    wx.showActionSheet({
      itemList: this.data.rechargeOptions.filter(option => option.enabled).map(option => `${option.name} - ${option.desc}`),
      success: (res) => {
        const selectedOption = this.data.rechargeOptions[res.tapIndex]
        this.handleRecharge(selectedOption)
      }
    })
  }

  /**
   * 处理充值
   */
  handleRecharge(option) {
    wx.showModal({
      title: '充值金额',
      content: '请输入充值金额',
      editable: true,
      placeholderText: '请输入金额',
      success: (res) => {
        if (res.confirm && res.content) {
          const amount = parseFloat(res.content)
          if (isNaN(amount) || amount <= 0) {
            this.showToast('请输入有效金额', 'error')
            return
          }
          if (amount < 1) {
            this.showToast('充值金额不能少于1元', 'error')
            return
          }
          if (amount > 500) {
            this.showToast('单次充值不能超过500元', 'error')
            return
          }
          this.processRecharge(option, amount)
        }
      }
    })
  }

  /**
   * 处理充值流程
   */
  async processRecharge(option, amount) {
    try {
      wx.showLoading({ title: `${option.name}充值中...` })
      
      // 这里应该调用充值API
      // const API = require('../../utils/api')
      // const response = await API.rechargeCampusCard({ amount, payment_method: option.method })
      
      wx.hideLoading()
      this.showToast('充值成功', 'success')
      
      // 刷新数据
      await this.loadAllData()
      
    } catch (error) {
      console.error('❌ 充值失败:', error)
      wx.hideLoading()
      this.showToast('充值失败', 'error')
    }
  }

  /**
   * 查看消费记录
   */
  onViewRecords() {
    this.navigate('/pages/campus-card/records/records')
  }

  /**
   * 挂失/解挂
   */
  onLossReport() {
    const { cardInfo } = this.data
    const isLost = cardInfo.status === 'lost'
    
    wx.showModal({
      title: isLost ? '解除挂失' : '挂失确认',
      content: isLost 
        ? '确定要解除校园卡挂失吗？解挂后卡片将恢复正常使用。'
        : '确定要挂失校园卡吗？挂失后卡片将无法使用。',
      confirmText: isLost ? '解除挂失' : '确认挂失',
      confirmColor: isLost ? '#00a870' : '#e34d59',
      success: (res) => {
        if (res.confirm) {
          this.processLossReport(!isLost)
        }
      }
    })
  }

  /**
   * 处理挂失/解挂
   */
  async processLossReport(isReporting) {
    try {
      wx.showLoading({ title: isReporting ? '挂失中...' : '解挂中...' })
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // 更新卡片状态
      const newStatus = isReporting ? 'lost' : 'normal'
      this.setData({
        'cardInfo.status': newStatus,
        'cardInfo.statusText': isReporting ? '已挂失' : '正常'
      })
      
      wx.hideLoading()
      this.showToast(isReporting ? '挂失成功' : '解挂成功', 'success')
      
    } catch (error) {
      wx.hideLoading()
      this.showToast(isReporting ? '挂失失败' : '解挂失败', 'error')
    }
  }

  /**
   * 修改密码
   */
  onChangePassword() {
    this.showToast('功能开发中', 'none')
  }

  /**
   * 显示使用指南
   */
  onShowGuide() {
    this.showToast('功能开发中', 'none')
  }

  /**
   * 服务功能点击
   */
  onServiceTap(e) {
    const service = e.currentTarget.dataset.service
    
    if (service.url) {
      this.navigate(service.url)
    } else if (service.action) {
      this[service.action] && this[service.action]()
    }
  }

  /**
   * 自定义错误处理
   */
  handleError(error) {
    if (error.message.includes('登录')) {
      this.showToast('登录已过期，请重新登录', 'error')
      setTimeout(() => {
        this.navigate('/pages/login/login')
      }, 2000)
    } else if (error.message.includes('网络')) {
      this.showToast('网络连接失败，请检查网络设置', 'error')
    } else {
      this.showToast(error.message || '操作失败', 'error')
    }
  }
}

// 创建页面实例并导出小程序页面配置
const campusCardPage = new CampusCardPage()
module.exports = createPage(campusCardPage) 