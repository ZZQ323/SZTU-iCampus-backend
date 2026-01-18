package cn.edu.sztui.base.infrastructure.util.cache.dto;

import lombok.Data;

import java.util.List;

@Data
public class ProxySession {
    private String wxCode;
    private List<String> userIds;
    private String cookiesJson;
    private long createTime;
    private long lastUpdateTime;
    private boolean loggedIn;
}
