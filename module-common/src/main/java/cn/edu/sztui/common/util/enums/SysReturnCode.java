package cn.edu.sztui.common.util.enums;

public enum SysReturnCode {
    ACCOUNT_OR_PASSWORD_ERROR(10001, "账号或密码错误"),
    ACCOUNT_LOCKOUT(10002, "该账号被禁用"),
    NO_LOGIN_AUTHORITY(10005, "没有登录访问权限"),
    NO_INTERFACE_AUTHORITY(10006, "没有权限对此接口访问"),
    CAPTCHA_EXPIRED(10010, "验证码过期"),
    CAPTCHA_ERROR(10011, "验证码输入错误"),
    OPERATION_UNSUCCESSFUL(10012, "此操作不成功"),
    OPERATION_NOT_ROLE(10013, "用户未绑定角色"),
    OPERATION_NOT_COMPANY(10014, "用户未绑定企业"),
    SENSITIVE_WORDS(10015, "敏感词汇不能使用"),
    INVALID_TOKEN(10016, "无效的token"),
    ACCOUNT_LOGIN_OTHER_TERMINAL(10017, "同一账号在另一客户端登陆"),
    TOKEN_REFRESH_TIMEOUT(10018, "已过刷新日期"),
    TOKEN_EXPIRATION(10019, "Token已过期"),
    TOKEN_PARSING_EXCEPTION(10020, "Token错误"),
    BASE_USR(1001, "用户服务"),
    BASE_SYS(1002, "系统服务"),
    BASE_BUILD(1003, "楼栋服务"),
    BASE_ENTERPRISE(1004, "企业服务"),
    BASE_COMMON(1005, "通用服务"),
    BASE_CUSTOMER(1006, "客户服务"),
    MIDDLE_USR(1201, "表单服务"),
    MIDDLE_SYS(1202, "流程应用服务"),
    MIDDLE_APPRO(1203, "流程审批服务"),
    MIDDLE_EVALUATE(1204, "评价管理"),
    MIDDLE_POINTS(1205, "积分服务"),
    MIDDLE_SMS(1206, "消息推送"),
    PEOPERTY_TIK(1301, "工单服务"),
    PEOPERTY_PATROL(1302, "巡更服务"),
    PEOPERTY_INSPECTION(1303, "核查服务"),
    PROPERTY_FLOW_SERVICE(1304, "物业服务"),
    PROPERTY_WAREHOUSE(2202, "仓库"),
    IOT_EQUIPMENT(1401, "设备服务"),
    IOT_ALERT(1402, "告警服务"),
    IOT_STORAGE(1403, "数据储存服务"),
    IOT_STATISTICS(1404, "数据统计服务"),
    IOT_STRATEGY(1405, "策略服务"),
    IOT_MESSAGE(1406, "消息中心"),
    IOT_CONFIGURATION(1407, "设备组态服务"),
    IOT_ENERYCONSUMPTION(1408, "能耗分析服务"),
    IOT_OPEN(1409, "openapi"),
    IOT_TOOL(1410, "图表工具服务"),
    IOT_METER(1411, "能源仪表服务"),
    IOT_CANTEEN(1412, "智慧食堂服务"),
    IOC_WEBSOCKET(1501, "websocket服务"),
    IOC_DATAVISUALZATION(1502, "可视化模型服务"),
    IOC_BIGSCREEN(1503, "可视化业务服务"),
    PASSING_VISIT(1601, "访客服务"),
    PASSING_PARK(1602, "停车场服务"),
    PASSING_PLATE_NULL(1603, "缺少必填参数车牌号码"),
    PASSING_RECORD_NULL(1604, "未查询出停车信息"),
    PASSING_FEE_NULL(1605, "未查询出费用"),
    PASSING_FEE_CHANGE(1606, "订单金额已经变更"),
    ASSET_BASE(1701, "资管服务"),
    RESOURCEBOOK_MEETINGROOM(1801, "会议室预定服务"),
    RESOURCEBOOK_BOX(1802, "包厢预定服务"),
    RESOURCEBOOK_CAR(1803, "车辆车位申请"),
    RESOURCEBOOK_MATERIAL(1804, "物资申请"),
    RESOURCEBOOK_COMMUNICATION(1805, "通信移机申请"),
    RESOURCEBOOK_STATION(1806, "工位申请"),
    RESOURCEBOOK_ACTIVITY_ROOM(1807, "活动室申请"),
    RESOURCE_INDENT_MANAGE(1808, "资源预定"),
    SHOP_CODE(2100, "店铺"),
    MALL_CODE(2101, "商城"),
    INFOINTER_ADVERTISE(1901, "信息互动广告服务"),
    EDGE_GATEWAY(2001, "硬件网关服务"),
    EDGE_INTEGRATION(2002, "集成服务"),
    EDGE_REGISTRY(2003, "设备注册服务"),
    PROJECT_PROJECT(2201, "项目管理服务");

    private final Integer code;
    private final String message;

    private SysReturnCode(Integer code, String message) {
        this.code = code;
        this.message = message;
    }

    public int code() {
        return this.code;
    }

    public String message() {
        return this.message;
    }

    public Integer getCode() {
        return this.code;
    }

    public String getMessage() {
        return this.message;
    }
}
