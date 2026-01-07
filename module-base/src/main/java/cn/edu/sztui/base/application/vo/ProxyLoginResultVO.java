package cn.edu.sztui.base.application.vo;

import lombok.Data;

/**
 * 代理登录结果
 */
@Data
public class ProxyLoginResultVO {

    private String machineId;
    private String userId;
    private boolean success;
    private String message;
}