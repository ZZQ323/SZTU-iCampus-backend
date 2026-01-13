package cn.edu.sztui.base.application.service.impl.proxy.lifespan;

import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class SessionValidator {

    @Resource
    private ProxySessionCacheUtil sessionCache;

    public boolean checkSession(String machineId) {
        String userId = sessionCache.getActiveAccount(machineId);
        if (userId == null) {
            return sessionCache.hasDeviceInitSession(machineId);
        }
        return checkSession(machineId, userId);
    }
    public boolean checkSession(String machineId, String userId) {
        if (!sessionCache.hasUserSession(machineId, userId)) {
            return false;
        }
        return true;
    }

}
