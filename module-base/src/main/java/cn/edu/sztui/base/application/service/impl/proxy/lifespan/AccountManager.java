package cn.edu.sztui.base.application.service.impl.proxy.lifespan;

import cn.edu.sztui.base.domain.model.proxy.SchoolHttpClient;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.Set;

@Slf4j
@Component
@RequiredArgsConstructor
public class AccountManager {

    private final SchoolHttpClient httpClient;
    private final ProxySessionCacheUtil sessionCache;

    public Set<String> getDeviceAccounts(String machineId) {
        return sessionCache.getValidDeviceAccounts(machineId);
    }

    public String getActiveAccount(String machineId) {
        return sessionCache.getActiveAccount(machineId);
    }

    public boolean switchAccount(String machineId, String userId) {
        return sessionCache.switchAccount(machineId, userId);
    }

    public void logout(String machineId, String userId) {
        log.info("登出, machineId: {}, userId: {}", machineId, userId);
        httpClient.clearUserCookies(machineId);
        sessionCache.removeUserSession(machineId, userId);
    }

    public void logout(String machineId) {
        String userId = sessionCache.getActiveAccount(machineId);
        if (userId != null) {
            logout(machineId, userId);
        } else {
            sessionCache.removeDeviceInitSession(machineId);
        }
        httpClient.clearUserCookies(machineId);
    }
}