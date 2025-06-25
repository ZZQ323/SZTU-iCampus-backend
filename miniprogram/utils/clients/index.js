/**
 * 业务客户端统一导出文件
 * 提供所有业务客户端的统一入口
 */

const AnnouncementClient = require('./AnnouncementClient')
const GradeClient = require('./GradeClient')
const CampusCardClient = require('./CampusCardClient')
const ScheduleClient = require('./ScheduleClient')
const EventClient = require('./EventClient')

// 创建客户端实例
const announcementClient = new AnnouncementClient()
const gradeClient = new GradeClient()
const campusCardClient = new CampusCardClient()
const scheduleClient = new ScheduleClient()
const eventClient = new EventClient()

module.exports = {
  // 客户端类
  AnnouncementClient,
  GradeClient,
  CampusCardClient,
  ScheduleClient,
  EventClient,
  
  // 客户端实例
  announcementClient,
  gradeClient,
  campusCardClient,
  scheduleClient,
  eventClient
} 