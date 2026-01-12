package cn.edu.sztui.base.application.vo;

import lombok.Builder;
import lombok.Data;

/**
 * 代理登录结果
 */
@Data
@Builder
public class ProxyLoginResultVO {

    private String machineId;
    private String userId;
    private boolean success;
    private boolean isNeedCaptcha;
    private String message;
}