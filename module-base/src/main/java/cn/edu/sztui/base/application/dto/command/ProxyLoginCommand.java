package cn.edu.sztui.base.application.dto.command;

import lombok.Data;

/**
 * 代理登录命令
 */
@Data
public class ProxyLoginCommand {
    /**
     * 机器ID（初始化时获取）
     */
    private String machineId;

    /**
     * 用户ID/学号
     */
    private String userId;

    /**
     * 验证码/密码/OTP
     */
    private String code;

    /**
     * 登录类型
     */
    private LoginType loginType;

    public enum LoginType {
        SMS,        // 短信验证码
        PASSWORD,   // 密码
        OTP         // 动态口令
    }
}
