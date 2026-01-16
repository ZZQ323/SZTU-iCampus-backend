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
    SENSITIVE_WORDS(10015, "敏感词汇不能使用"),
    INVALID_COOKIE(10016, "无效的Cookie"),
    ACCOUNT_LOGIN_OTHER_TERMINAL(10017, "同一账号在另一客户端登陆"),
    COOKIE_REFRESH_TIMEOUT(10018, "已过刷新日期"),
    COOKIE_EXPIRATION(10019, "Cookie已过期"),
    COOKIE_PARSING_EXCEPTION(10020, "Cookie错误"),
    BASE_USR(1001, "用户服务"),
    BASE_PROXY(1002, "代理服务"),
    WECHAT_PROXY(2001, "微信API"),
    BASE_SYS(1003, "系统服务");

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
