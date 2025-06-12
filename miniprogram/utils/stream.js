/**
 * 流式数据处理工具类
 * 用于处理实时数据流，提升用户体验
 */
class StreamManager {
  constructor() {
    this.connections = new Map(); // 存储活跃的流式连接
    this.listeners = new Map();   // 存储事件监听器
  }

  /**
   * 连接流式数据源
   * @param {string} streamId 流ID
   * @param {string} url 流式API地址
   * @param {function} onData 数据回调函数
   * @param {function} onError 错误回调函数
   */
  connect(streamId, url, onData, onError) {
    const app = getApp();
    
    // 如果已存在连接，先断开
    if (this.connections.has(streamId)) {
      this.disconnect(streamId);
    }

    console.log(`[StreamManager] 连接流式数据源: ${streamId}`);
    
    const requestTask = wx.request({
      url: `${app.globalData.baseUrl}${url}`,
      header: {
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache'
      },
      enableChunked: true,
      success: (res) => {
        if (res.statusCode === 200) {
          this.processStreamData(res.data, onData);
        }
      },
      fail: (error) => {
        console.error(`[StreamManager] 连接失败:`, error);
        if (onError) onError(error);
      }
    });

    // 存储连接任务
    this.connections.set(streamId, requestTask);
    
    return requestTask;
  }

  /**
   * 处理流式数据
   * @param {string} streamData 流式数据
   * @param {function} onData 数据处理回调
   */
  processStreamData(streamData, onData) {
    if (!streamData) return;

    // 处理 Server-Sent Events 格式数据
    const lines = streamData.split('\n');
    
    for (let line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const jsonData = line.substring(6); // 移除 'data: ' 前缀
          const data = JSON.parse(jsonData);
          
          // 调用数据处理回调
          if (onData) {
            onData(data);
          }
        } catch (error) {
          console.error('[StreamManager] 数据解析失败:', error);
        }
      }
    }
  }

  /**
   * 断开流式连接
   * @param {string} streamId 流ID
   */
  disconnect(streamId) {
    const connection = this.connections.get(streamId);
    if (connection) {
      connection.abort();
      this.connections.delete(streamId);
      console.log(`[StreamManager] 断开连接: ${streamId}`);
    }
  }

  /**
   * 断开所有连接
   */
  disconnectAll() {
    for (let [streamId, connection] of this.connections) {
      connection.abort();
    }
    this.connections.clear();
    console.log('[StreamManager] 断开所有连接');
  }

  /**
   * 添加事件监听器
   * @param {string} event 事件名称
   * @param {function} callback 回调函数
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * 触发事件
   * @param {string} event 事件名称
   * @param {any} data 事件数据
   */
  emit(event, data) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  /**
   * 移除事件监听器
   * @param {string} event 事件名称
   * @param {function} callback 回调函数
   */
  off(event, callback) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }
}

// 创建全局实例
const streamManager = new StreamManager();

/**
 * 流式公告管理器
 */
class AnnouncementStream {
  constructor() {
    this.streamId = 'announcements';
  }

  /**
   * 开始监听公告流
   * @param {function} onNewAnnouncement 新公告回调
   */
  start(onNewAnnouncement) {
    streamManager.connect(
      this.streamId,
      '/api/announcements/stream',
      (data) => {
        console.log('[AnnouncementStream] 收到新公告:', data);
        if (onNewAnnouncement) {
          onNewAnnouncement(data);
        }
        
        // 触发全局事件
        streamManager.emit('newAnnouncement', data);
      },
      (error) => {
        console.error('[AnnouncementStream] 连接错误:', error);
      }
    );
  }

  stop() {
    streamManager.disconnect(this.streamId);
  }
}

/**
 * 流式活动管理器
 */
class EventStream {
  constructor() {
    this.streamId = 'events';
  }

  /**
   * 开始监听活动流
   * @param {function} onEventUpdate 活动更新回调
   */
  start(onEventUpdate) {
    streamManager.connect(
      this.streamId,
      '/api/events/stream',
      (data) => {
        console.log('[EventStream] 活动数据更新:', data);
        if (onEventUpdate) {
          onEventUpdate(data);
        }
        
        // 触发全局事件
        streamManager.emit('eventUpdate', data);
      },
      (error) => {
        console.error('[EventStream] 连接错误:', error);
      }
    );
  }

  stop() {
    streamManager.disconnect(this.streamId);
  }
}

// 导出工具类
module.exports = {
  StreamManager,
  streamManager,
  AnnouncementStream,
  EventStream
}; 