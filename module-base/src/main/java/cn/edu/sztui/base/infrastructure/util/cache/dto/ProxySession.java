package cn.edu.sztui.base.infrastructure.util.cache.dto;

import lombok.Data;

@Data
public class ProxySession {
    private String wxCode;
    private String userId;
    private String cookiesJson;
    private long createTime;
    private long lastUpdateTime;
    private boolean loggedIn;
}
