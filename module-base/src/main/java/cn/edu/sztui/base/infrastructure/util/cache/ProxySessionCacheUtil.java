package cn.edu.sztui.base.infrastructure.util.cache;

import cn.edu.sztui.common.cache.util.CacheUtil;
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONArray;
import jakarta.annotation.Resource;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.hc.client5.http.cookie.Cookie;
import org.apache.hc.client5.http.impl.cookie.BasicClientCookie;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

/**
 * 代理会话缓存工具
 *
 * 存储结构：
 * - proxy:machine:{machineId} -> ProxySession (机器初始会话)
 * - proxy:user:{userId} -> machineId (用户到机器的映射)
 */
@Slf4j
@Component
public class ProxySessionCacheUtil {

    private static final String MACHINE_SESSION_KEY = "proxy:machine:";
    private static final String USER_MAPPING_KEY = "proxy:user:";

    // 机器会话过期时间 30分钟
    private static final long MACHINE_SESSION_EXPIRE = 1800;
    // 登录会话过期时间 10分钟
    private static final long LOGIN_SESSION_EXPIRE = 600;

    @Resource
    private CacheUtil cacheUtil;

    /**
     * 生成机器ID，前端完成
     */
    @Deprecated
    public String generateMachineId() {
        return UUID.randomUUID().toString().replace("-", "");
    }

    /**
     * 保存机器初始会话（登录前）
     */
    public void saveMachineSession(String machineId, List<Cookie> cookies) {
        if (!StringUtils.hasText(machineId) || CollectionUtils.isEmpty(cookies)) {
            return;
        }
        ProxySession session = new ProxySession();
        session.setMachineId(machineId);
        session.setCookiesJson(serializeCookies(cookies));
        session.setCreateTime(Instant.now().toEpochMilli());
        session.setLastUpdateTime(Instant.now().toEpochMilli());

        cacheUtil.hset(MACHINE_SESSION_KEY + machineId, JSON.toJSONString(session), MACHINE_SESSION_EXPIRE);
        log.info("保存机器会话: {}", machineId);
    }

    /**
     * 绑定用户到机器会话（登录成功后）
     */
    public void bindUserToMachine(String machineId, String userId, List<Cookie> newCookies) {
        ProxySession session = getMachineSession(machineId);
        if (session == null) {
            session = new ProxySession();
            session.setMachineId(machineId);
            session.setCreateTime(Instant.now().toEpochMilli());
        }

        session.setUserId(userId);
        session.setCookiesJson(serializeCookies(newCookies));
        session.setLastUpdateTime(Instant.now().toEpochMilli());
        session.setLoggedIn(true);

        // 更新机器会话（延长过期时间）
        cacheUtil.hset(MACHINE_SESSION_KEY + machineId, JSON.toJSONString(session), LOGIN_SESSION_EXPIRE);

        // 创建用户到机器的映射
        cacheUtil.hset(USER_MAPPING_KEY + userId, machineId, LOGIN_SESSION_EXPIRE);

        log.info("用户 {} 绑定到机器 {}", userId, machineId);
    }

    /**
     * 更新会话Cookie（访问API后）
     */
    public void updateSessionCookies(String machineId, List<Cookie> cookies) {
        ProxySession session = getMachineSession(machineId);
        if (session == null) {
            log.warn("机器会话不存在: {}", machineId);
            return;
        }

        session.setCookiesJson(serializeCookies(cookies));
        session.setLastUpdateTime(Instant.now().toEpochMilli());

        long expire = session.isLoggedIn() ? LOGIN_SESSION_EXPIRE : MACHINE_SESSION_EXPIRE;
        cacheUtil.hset(MACHINE_SESSION_KEY + machineId, JSON.toJSONString(session), expire);
    }

    /**
     * 获取机器会话
     */
    public ProxySession getMachineSession(String machineId) {
        if (!StringUtils.hasText(machineId)) {
            return null;
        }
        Object obj = cacheUtil.hget(MACHINE_SESSION_KEY , machineId);
        if (obj == null) {
            return null;
        }
        return JSON.parseObject(obj.toString(), ProxySession.class);
    }

    /**
     * 通过用户ID获取会话
     */
    public ProxySession getSessionByUserId(String userId) {
        if (!StringUtils.hasText(userId)) {
            return null;
        }
        Object machineIdObj = cacheUtil.hget(USER_MAPPING_KEY , userId);
        if (machineIdObj == null) {
            return null;
        }
        return getMachineSession(machineIdObj.toString());
    }

    /**
     * 获取会话中的Cookies
     */
    public List<Cookie> getSessionCookies(String machineId) {
        ProxySession session = getMachineSession(machineId);
        if (session == null || !StringUtils.hasText(session.getCookiesJson())) {
            return Collections.emptyList();
        }
        return deserializeCookies(session.getCookiesJson());
    }

    /**
     * 检查机器会话是否有效
     */
    public boolean hasMachineSession(String machineId) {
        return cacheUtil.hHasKey(MACHINE_SESSION_KEY , machineId);
    }

    /**
     * 检查是否已登录
     */
    public boolean isLoggedIn(String machineId) {
        ProxySession session = getMachineSession(machineId);
        return session != null && session.isLoggedIn();
    }

    /**
     * 删除会话（登出）
     */
    public void removeSession(String machineId) {
        ProxySession session = getMachineSession(machineId);
        if (session != null && StringUtils.hasText(session.getUserId())) {
            cacheUtil.del(USER_MAPPING_KEY + session.getUserId());
        }
        cacheUtil.del(MACHINE_SESSION_KEY + machineId);
        log.info("删除机器会话: {}", machineId);
    }

    /**
     * 通过用户ID删除会话
     */
    public void removeSessionByUserId(String userId) {
        Object machineIdObj = cacheUtil.hget (USER_MAPPING_KEY , userId);
        if (machineIdObj != null) {
            removeSession(machineIdObj.toString());
        }
        cacheUtil.del(USER_MAPPING_KEY + userId);
    }

    // ==================== Cookie序列化 ====================

    private String serializeCookies(List<Cookie> cookies) {
        List<CookieDTO> dtos = cookies.stream()
                .map(c -> {
                    CookieDTO dto = new CookieDTO();
                    dto.setName(c.getName());
                    dto.setValue(c.getValue());
                    dto.setDomain(c.getDomain());
                    dto.setPath(c.getPath());
                    if (c.getExpiryInstant() != null) {
                        dto.setExpiryTime(c.getExpiryInstant().toEpochMilli());
                    }
                    dto.setSecure(c.isSecure());
                    return dto;
                })
                .toList();
        return JSON.toJSONString(dtos);
    }

    private List<Cookie> deserializeCookies(String json) {
        List<CookieDTO> dtos = JSONArray.parseArray(json, CookieDTO.class);
        return dtos.stream()
                .map(dto -> {
                    BasicClientCookie cookie = new BasicClientCookie(dto.getName(), dto.getValue());
                    cookie.setDomain(dto.getDomain());
                    cookie.setPath(dto.getPath());
                    cookie.setSecure(dto.isSecure());
                    if (dto.getExpiryTime() != null) {
                        cookie.setExpiryDate(Instant.ofEpochMilli(dto.getExpiryTime()));
                    }
                    return (Cookie) cookie;
                })
                .toList();
    }

    // ==================== 内部数据类 ====================

    @Data
    public static class ProxySession {
        private String machineId;
        private String userId;
        private String cookiesJson;
        private long createTime;
        private long lastUpdateTime;
        private boolean loggedIn;
    }

    @Data
    public static class CookieDTO {
        private String name;
        private String value;
        private String domain;
        private String path;
        private Long expiryTime;
        private boolean secure;
    }
}
