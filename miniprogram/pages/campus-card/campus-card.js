Page({
  data: {
    userInfo: {
      name: '张三',
      studentId: '2024001',
      avatar: '/assets/images/avatar.png'
    },
    balance: '256.80',
    transactions: []
  },

  onLoad() {
    this.loadTransactions();
  },

  loadTransactions() {
    // 模拟数据，实际项目中应该从后端API获取
    this.setData({
      transactions: [
        {
          id: 1,
          merchant: '第一食堂',
          amount: '12.50',
          time: '2024-01-15 12:30',
          type: 'expense'
        },
        {
          id: 2,
          merchant: '校园卡充值',
          amount: '100.00',
          time: '2024-01-14 15:20',
          type: 'income'
        },
        {
          id: 3,
          merchant: '图书馆打印',
          amount: '2.00',
          time: '2024-01-14 10:15',
          type: 'expense'
        }
      ]
    });
  }
}); 