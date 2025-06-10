Page({
  data: {
    totalBooks: '500,000',
    borrowedBooks: []
  },

  onLoad() {
    this.loadBorrowedBooks();
  },

  loadBorrowedBooks() {
    // 模拟数据，实际项目中应该从后端API获取
    this.setData({
      borrowedBooks: [
        {
          id: 1,
          title: '人工智能：一种现代方法',
          author: 'Stuart Russell',
          dueDate: '2024-02-15'
        },
        {
          id: 2,
          title: '深入理解计算机系统',
          author: 'Randal E. Bryant',
          dueDate: '2024-02-20'
        },
        {
          id: 3,
          title: '算法导论',
          author: 'Thomas H. Cormen',
          dueDate: '2024-02-25'
        }
      ]
    });
  }
}); 