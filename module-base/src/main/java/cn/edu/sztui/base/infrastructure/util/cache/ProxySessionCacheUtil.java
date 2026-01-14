package cn.edu.sztui.base.infrastructure.util.cache;

import cn.edu.sztui.common.cache.util.CacheUtil;
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONArray;
import jakarta.annotation.Resource;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.cookie.Cookie;
import org.apache.http.impl.cookie.BasicClientCookie;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

import java.time.Instant;
import java.util.*;

/**
 * 代理会话缓存工具 - 重新设计版本
 *
 * <h2>设计理念</h2>
 * <p>分离三层概念：</p>
 * <ul>
 *   <li><b>设备初始化会话</b>：machineId → 初始化时的临时 cookie（短期，仅用于登录流程）</li>
 *   <li><b>用户登录会话</b>：machineId:userId → 登录后的 cookie（长期，用于 API 访问）</li>
 *   <li><b>设备账号管理</b>：machineId → 已登录的 userId 列表（用于账号切换）</li>
 * </ul>
 *
 * <h2>缓存结构</h2>
 * <pre>
 * # 1. 设备初始化会话（临时，用于登录流程，30分钟过期）
 * proxy:device:init:{machineId} → DeviceInitSession { cookies, createTime }
 *
 * # 2. 用户登录会话（核心，登录成功后使用，可配置较长过期时间）
 * proxy:session:{machineId}:{userId} → UserSession { cookies, loginTime, lastAccess }
 *
 * # 3. 设备上的已登录账号列表（用于账号切换功能）
 * proxy:device:accounts:{machineId} → Set&lt;userId&gt;
 *
 * # 4. 设备当前活跃账号（记录当前正在使用的账号）
 * proxy:device:active:{machineId} → userId
 * </pre>
 *
 * <h2>典型流程</h2>
 * <ol>
 *   <li>initSession: 写入 device:init</li>
 *   <li>sendSms: 使用并更新 device:init</li>
 *   <li>login成功: 删除 device:init，创建 session:{machineId}:{userId}，更新 accounts 和 active</li>
 *   <li>proxyApi: 使用 session:{machineId}:{userId}</li>
 *   <li>switchAccount: 更新 active</li>
 *   <li>logout: 删除对应 session，从 accounts 移除</li>
 * </ol>
 *
 * <h2>安全考虑</h2>
 * <ul>
 *   <li>Cookie 仅存储在 Redis，前端只持有 machineId</li>
 *   <li>访问 session 需要同时提供 machineId 和 userId</li>
 *   <li>不同设备的会话完全隔离</li>
 * </ul>
 */
@Slf4j
@Component
public class ProxySessionCacheUtil {

    // ==================== 缓存键前缀 ====================

    /**
     * 设备初始化会话键前缀
     */
    private static final String KEY_DEVICE_INIT = "proxy:device:init:";

    /**
     * 用户登录会话键前缀
     */
    private static final String KEY_SESSION = "proxy:session:";

    /**
     * 设备账号列表键前缀
     */
    private static final String KEY_DEVICE_ACCOUNTS = "proxy:device:accounts:";

    /**
     * 设备当前活跃账号键前缀
     */
    private static final String KEY_DEVICE_ACTIVE = "proxy:device:active:";

    // ==================== 过期时间配置 ====================

    /**
     * 设备初始化会话过期时间：30分钟（仅用于登录流程）
     */
    private static final long DEVICE_INIT_EXPIRE = 1800;

    /**
     * 用户登录会话过期时间：7天（可根据需求调整）
     */
    private static final long USER_SESSION_EXPIRE = 7 * 24 * 3600;

    /**
     * 设备账号列表过期时间：30天
     */
    private static final long DEVICE_ACCOUNTS_EXPIRE = 30 * 24 * 3600;

    @Resource
    private CacheUtil cacheUtil;

    // ==================== 1. 设备初始化会话管理 ====================

    /**
     * 保存设备初始化会话
     * <p>在 initSession 阶段调用，存储访问网关获取的初始 Cookie</p>
     *
     * @param machineId 设备唯一标识
     * @param cookies   初始化获取的 Cookie 列表
     */
    public void saveDeviceInitSession(String machineId, List<Cookie> cookies) {
        if (!StringUtils.hasText(machineId) || CollectionUtils.isEmpty(cookies)) {
            log.warn("保存设备初始化会话失败: machineId 或 cookies 为空");
            return;
        }
        DeviceInitSession session = new DeviceInitSession();
        session.setCookiesJson(serializeCookies(cookies));
        session.setCreateTime(Instant.now().toEpochMilli());
        cacheUtil.hset(KEY_DEVICE_INIT, machineId, JSON.toJSONString(session), DEVICE_INIT_EXPIRE);
        log.info("保存设备初始化会话: machineId={} , session 写入{}", machineId, JSON.toJSONString(session));
    }

    /**
     * 获取设备初始化会话
     *
     * @param machineId 设备唯一标识
     * @return 初始化会话，不存在则返回 null
     */
    public DeviceInitSession getDeviceInitSession(String machineId) {
        if (!StringUtils.hasText(machineId))return null;
        Object obj = cacheUtil.hget(KEY_DEVICE_INIT, machineId);
        if (obj == null) return null;
        return JSON.parseObject(obj.toString(), DeviceInitSession.class);
    }

    /**
     * 获取设备初始化会话的 Cookies
     *
     * @param machineId 设备唯一标识
     * @return Cookie 列表，不存在则返回空列表
     */
    public List<Cookie> getDeviceInitCookies(String machineId) {
        DeviceInitSession session = getDeviceInitSession(machineId);
        if (session == null || !StringUtils.hasText(session.getCookiesJson())) {
            return Collections.emptyList();
        }
        return deserializeCookies(session.getCookiesJson());
    }

    /**
     * 更新设备初始化会话的 Cookies
     * <p>在 sendSms 阶段调用，服务器可能返回新的 Cookie</p>
     *
     * @param machineId 设备唯一标识
     * @param cookies   新的 Cookie 列表
     */
    public void updateDeviceInitCookies(String machineId, List<Cookie> cookies) {
        DeviceInitSession session = getDeviceInitSession(machineId);
        if (session == null) {
            log.warn("更新设备初始化会话失败: 会话不存在, machineId={}", machineId);
            return;
        }
        DeviceInitSession oldSession = JSON.parseObject((String) cacheUtil.hget(KEY_DEVICE_INIT, machineId), DeviceInitSession.class);
        List<Cookie> oldCookies = deserializeCookies(oldSession.getCookiesJson());

        HashSet<Cookie> set = new HashSet<>();
        for (Cookie ele : cookies) set.add(ele);
        for (Cookie ele : oldCookies) set.add(ele);
        List<Cookie> newCookies = set.stream().toList();

        session.setCookiesJson(serializeCookies(newCookies));

        cacheUtil.hset(KEY_DEVICE_INIT, machineId, JSON.toJSONString(session), DEVICE_INIT_EXPIRE);
        log.info("更新设备初始化会话 Cookies: machineId={}", machineId);
    }

    /**
     * 检查设备初始化会话是否存在
     *
     * @param machineId 设备唯一标识
     * @return true 如果存在
     */
    public boolean hasDeviceInitSession(String machineId) {
        if (!StringUtils.hasText(machineId)) {
            return false;
        }
        return cacheUtil.hHasKey(KEY_DEVICE_INIT, machineId);
    }

    /**
     * 删除设备初始化会话
     * <p>登录成功后调用，清理临时会话</p>
     *
     * @param machineId 设备唯一标识
     */
    public void removeDeviceInitSession(String machineId) {
        if (StringUtils.hasText(machineId)) {
            cacheUtil.hdel(KEY_DEVICE_INIT, machineId);
            log.debug("删除设备初始化会话: machineId={}", machineId);
        }
    }

    // ==================== 2. 用户登录会话管理 ====================

    /**
     * 创建用户登录会话
     * <p>登录成功后调用，存储登录后的 Cookie</p>
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     * @param cookies   登录后的 Cookie 列表
     */
    public void createUserSession(String machineId, String userId, List<Cookie> cookies) {
        if (!StringUtils.hasText(machineId) || !StringUtils.hasText(userId)) {
            log.warn("创建用户会话失败: machineId 或 userId 为空");
            return;
        }
        UserSession session = new UserSession();
        session.setMachineId(machineId);
        session.setUserId(userId);
        session.setCookiesJson(serializeCookies(cookies));
        session.setLoginTime(Instant.now().toEpochMilli());
        session.setLastAccessTime(Instant.now().toEpochMilli());
        // 1. 保存用户会话
        cacheUtil.hset(KEY_SESSION, machineId + ":" + userId, JSON.toJSONString(session), USER_SESSION_EXPIRE);
        // 2. 添加到设备账号列表
        addToDeviceAccounts(machineId, userId);
        // 3. 设置为当前活跃账号
        setActiveAccount(machineId, userId);
        // 4. 清理设备初始化会话（登录流程结束）
        removeDeviceInitSession(machineId);
        log.info("创建用户登录会话: machineId={}, userId={}", machineId, userId);
    }

    /**
     * 获取用户登录会话
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     * @return 用户会话，不存在则返回 null
     */
    public UserSession getUserSession(String machineId, String userId) {
        if (!StringUtils.hasText(machineId) || !StringUtils.hasText(userId)) {
            return null;
        }
        Object obj = cacheUtil.hget(KEY_SESSION, machineId + ":" + userId);
        if (obj == null) {
            return null;
        }
        return JSON.parseObject(obj.toString(), UserSession.class);
    }

    /**
     * 获取用户登录会话的 Cookies
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     * @return Cookie 列表，不存在则返回空列表
     */
    public List<Cookie> getUserSessionCookies(String machineId, String userId) {
        UserSession session = getUserSession(machineId, userId);
        if (session == null || !StringUtils.hasText(session.getCookiesJson())) {
            return Collections.emptyList();
        }
        return deserializeCookies(session.getCookiesJson());
    }

    /**
     * 更新用户会话的 Cookies
     * <p>每次 API 请求后调用，保持 Cookie 最新</p>
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     * @param cookies   新的 Cookie 列表
     */
    public void updateUserSessionCookies(String machineId, String userId, List<Cookie> cookies) {
        UserSession session = getUserSession(machineId, userId);
        if (session == null) {
            log.warn("更新用户会话失败: 会话不存在, machineId={}, userId={}", machineId, userId);
            return;
        }

        session.setCookiesJson(serializeCookies(cookies));
        session.setLastAccessTime(Instant.now().toEpochMilli());
        cacheUtil.hset(KEY_SESSION, machineId + ":" + userId, JSON.toJSONString(session), USER_SESSION_EXPIRE);
        log.debug("更新用户会话 Cookies: machineId={}, userId={}", machineId, userId);
    }

    /**
     * 刷新用户会话的最后访问时间
     * <p>延长会话有效期</p>
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     */
    public void touchUserSession(String machineId, String userId) {
        UserSession session = getUserSession(machineId, userId);
        if (session == null) {
            return;
        }
        session.setLastAccessTime(Instant.now().toEpochMilli());
        cacheUtil.hset(KEY_SESSION, machineId + ":" + userId, JSON.toJSONString(session), USER_SESSION_EXPIRE);
    }

    /**
     * 检查用户会话是否存在
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     * @return true 如果存在
     */
    public boolean hasUserSession(String machineId, String userId) {
        if (!StringUtils.hasText(machineId) || !StringUtils.hasText(userId)) {
            return false;
        }
        return cacheUtil.hHasKey(KEY_SESSION, machineId + ":" + userId);
    }

    /**
     * 删除用户会话（登出）
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     */
    public void removeUserSession(String machineId, String userId) {
        if (!StringUtils.hasText(machineId) || !StringUtils.hasText(userId)) {
            return;
        }

        // 1. 删除会话
        cacheUtil.hdel(KEY_SESSION, machineId + ":" + userId);

        // 2. 从设备账号列表移除
        removeFromDeviceAccounts(machineId, userId);

        // 3. 如果是当前活跃账号，清除活跃状态
        String activeUserId = getActiveAccount(machineId);
        if (userId.equals(activeUserId)) {
            clearActiveAccount(machineId);
        }

        log.info("删除用户会话: machineId={}, userId={}", machineId, userId);
    }

    // ==================== 3. 设备账号列表管理 ====================

    /**
     * 添加账号到设备账号列表
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     */
    private void addToDeviceAccounts(String machineId, String userId) {
        Set<String> accounts = getDeviceAccounts(machineId);
        accounts.add(userId);
        cacheUtil.hset(KEY_DEVICE_ACCOUNTS, machineId, JSON.toJSONString(accounts), DEVICE_ACCOUNTS_EXPIRE);
    }

    /**
     * 从设备账号列表移除
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     */
    private void removeFromDeviceAccounts(String machineId, String userId) {

        Set<String> accounts = getDeviceAccounts(machineId);
        accounts.remove(userId);

        if (accounts.isEmpty()) {
            cacheUtil.hdel(KEY_DEVICE_ACCOUNTS, machineId);
        } else {
            cacheUtil.hset(KEY_DEVICE_ACCOUNTS, machineId, JSON.toJSONString(accounts), DEVICE_ACCOUNTS_EXPIRE);
        }
    }

    /**
     * 获取设备上的所有已登录账号
     *
     * @param machineId 设备唯一标识
     * @return 用户ID 集合
     */
    public Set<String> getDeviceAccounts(String machineId) {
        if (!StringUtils.hasText(machineId)) {
            return new HashSet<>();
        }
        Object obj = cacheUtil.hget(KEY_DEVICE_ACCOUNTS, machineId);
        if (obj == null) {
            return new HashSet<>();
        }

        List<String> list = JSONArray.parseArray(obj.toString(), String.class);
        return new HashSet<>(list);
    }

    /**
     * 获取设备上所有有效的已登录账号
     * <p>会验证每个账号的会话是否仍然有效</p>
     *
     * @param machineId 设备唯一标识
     * @return 有效的用户ID 集合
     */
    public Set<String> getValidDeviceAccounts(String machineId) {
        Set<String> accounts = getDeviceAccounts(machineId);
        Set<String> validAccounts = new HashSet<>();

        for (String userId : accounts) {
            if (hasUserSession(machineId, userId)) {
                validAccounts.add(userId);
            }
        }

        // 清理无效账号
        if (validAccounts.size() != accounts.size()) {
            if (validAccounts.isEmpty()) {
                cacheUtil.hdel(KEY_DEVICE_ACCOUNTS, machineId);
            } else {
                cacheUtil.hset(KEY_DEVICE_ACCOUNTS, machineId, JSON.toJSONString(validAccounts), DEVICE_ACCOUNTS_EXPIRE);
            }
        }

        return validAccounts;
    }

    // ==================== 4. 设备活跃账号管理 ====================

    /**
     * 设置设备当前活跃账号
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     */
    public void setActiveAccount(String machineId, String userId) {
        if (!StringUtils.hasText(machineId) || !StringUtils.hasText(userId)) {
            return;
        }

        cacheUtil.hset(KEY_DEVICE_ACTIVE, machineId, userId, DEVICE_ACCOUNTS_EXPIRE);
        log.debug("设置活跃账号: machineId={}, userId={}", machineId, userId);
    }

    /**
     * 获取设备当前活跃账号
     *
     * @param machineId 设备唯一标识
     * @return 当前活跃的用户ID，不存在则返回 null
     */
    public String getActiveAccount(String machineId) {
        if (!StringUtils.hasText(machineId)) {
            return null;
        }
        Object obj = cacheUtil.hget(KEY_DEVICE_ACTIVE, machineId);
        return obj != null ? obj.toString() : null;
    }

    /**
     * 清除设备活跃账号
     *
     * @param machineId 设备唯一标识
     */
    public void clearActiveAccount(String machineId) {
        if (StringUtils.hasText(machineId)) {
            cacheUtil.hdel(KEY_DEVICE_ACTIVE, machineId);
        }
    }

    /**
     * 切换设备活跃账号
     * <p>切换到另一个已登录的账号</p>
     *
     * @param machineId 设备唯一标识
     * @param userId    目标用户ID
     * @return true 如果切换成功
     */
    public boolean switchAccount(String machineId, String userId) {
        // 验证目标账号会话存在
        if (!hasUserSession(machineId, userId)) {
            log.warn("切换账号失败: 目标会话不存在, machineId={}, userId={}", machineId, userId);
            return false;
        }

        setActiveAccount(machineId, userId);
        log.info("切换账号成功: machineId={}, userId={}", machineId, userId);
        return true;
    }

    // ==================== 5. 便捷方法 ====================

    /**
     * 获取当前活跃会话的 Cookies
     * <p>便捷方法：自动使用当前活跃账号</p>
     *
     * @param machineId 设备唯一标识
     * @return Cookie 列表，不存在则返回空列表
     */
    public List<Cookie> getActiveSessionCookies(String machineId) {
        String userId = getActiveAccount(machineId);
        if (userId == null) {
            return Collections.emptyList();
        }
        return getUserSessionCookies(machineId, userId);
    }

    /**
     * 获取当前活跃会话
     * <p>便捷方法：自动使用当前活跃账号</p>
     *
     * @param machineId 设备唯一标识
     * @return 用户会话，不存在则返回 null
     */
    public UserSession getActiveSession(String machineId) {
        String userId = getActiveAccount(machineId);
        if (userId == null) {
            return null;
        }
        return getUserSession(machineId, userId);
    }

    /**
     * 清理设备所有数据
     * <p>完全清除设备相关的所有缓存</p>
     *
     * @param machineId 设备唯一标识
     */
    public void clearDeviceAllData(String machineId) {
        if (!StringUtils.hasText(machineId)) {
            return;
        }

        // 1. 删除所有用户会话
        Set<String> accounts = getDeviceAccounts(machineId);
        for (String userId : accounts) {
            cacheUtil.hdel(KEY_SESSION, machineId + ":" + userId);
        }

        // 2. 删除设备初始化会话
        removeDeviceInitSession(machineId);

        // 3. 删除账号列表
        cacheUtil.hdel(KEY_DEVICE_ACCOUNTS, machineId);

        // 4. 删除活跃账号
        cacheUtil.hdel(KEY_DEVICE_ACTIVE, machineId);

        log.info("清理设备所有数据: machineId={}", machineId);
    }

    // ==================== 私有辅助方法 ====================


    /**
     * 序列化 Cookie 列表为 JSON
     */
    private String serializeCookies(List<Cookie> cookies) {
        if (CollectionUtils.isEmpty(cookies)) {
            return "[]";
        }
        List<CookieDTO> dtos = cookies.stream()
            .map(c -> {
                CookieDTO dto = new CookieDTO();
                dto.setName(c.getName());
                dto.setValue(c.getValue());
                dto.setDomain(c.getDomain());
                if(Objects.isNull(c.getDomain()))
                    dto.setDomain("webvpn.sztu.edu.cn");
                dto.setPath(c.getPath());
                if (c.getExpiryDate() != null) {
                    dto.setExpiryTime(c.getExpiryDate().getTime());
                }
                dto.setSecure(c.isSecure());
                return dto;
            })
            .toList();
        return JSON.toJSONString(dtos);
    }

    /**
     * 反序列化 JSON 为 Cookie 列表
     */
    private List<Cookie> deserializeCookies(String json) {
        if (!StringUtils.hasText(json) || "[]".equals(json)) {
            return Collections.emptyList();
        }

        List<CookieDTO> dtos = JSONArray.parseArray(json, CookieDTO.class);
        return dtos.stream()
                .map(dto -> {
                    BasicClientCookie cookie = new BasicClientCookie(dto.getName(), dto.getValue());
                    cookie.setDomain(dto.getDomain());
                    cookie.setPath(dto.getPath());
                    cookie.setSecure(dto.isSecure());
                    if (dto.getExpiryTime() != null) {
                        cookie.setExpiryDate(Date.from(Instant.ofEpochSecond(dto.getExpiryTime())));
                    }
                    return (Cookie) cookie;
                })
                .toList();
    }

    // ==================== 内部数据类 ====================

    /**
     * 设备初始化会话
     * <p>临时存储，仅用于登录流程</p>
     */
    @Data
    public static class DeviceInitSession {
        /**
         * Cookie JSON
         */
        private String cookiesJson;
        /**
         * 创建时间
         */
        private long createTime;
    }

    /**
     * 用户登录会话
     * <p>核心存储，用于已登录用户的 API 访问</p>
     */
    @Data
    public static class UserSession {
        /**
         * 设备ID
         */
        private String machineId;
        /**
         * 用户ID
         */
        private String userId;
        /**
         * Cookie JSON
         */
        private String cookiesJson;
        /**
         * 登录时间
         */
        private long loginTime;
        /**
         * 最后访问时间
         */
        private long lastAccessTime;
    }

    /**
     * Cookie 数据传输对象
     * <p>用于序列化/反序列化</p>
     */
    @Data
    public static class CookieDTO {
        private String name;
        private String value;
        private String domain;
        private String path;
        private Long expiryTime;
        private boolean secure;
    }

    // ==================== 兼容旧接口（可选，逐步废弃） ====================

    /**
     * @deprecated 使用 {@link #saveDeviceInitSession(String, List)} 代替
     */
    @Deprecated
    public void saveMachineSession(String machineId, List<Cookie> cookies) {
        saveDeviceInitSession(machineId, cookies);
    }

    /**
     * @deprecated 使用 {@link #hasDeviceInitSession(String)} 代替
     */
    @Deprecated
    public boolean hasMachineSession(String machineId) {
        return hasDeviceInitSession(machineId);
    }

    /**
     * @deprecated 使用 {@link #getDeviceInitCookies(String)} 或 {@link #getUserSessionCookies(String, String)} 代替
     */
    @Deprecated
    public List<Cookie> getSessionCookies(String machineId) {
        // 优先返回活跃用户的 cookie，否则返回初始化 cookie
        List<Cookie> cookies = getActiveSessionCookies(machineId);
        if (!cookies.isEmpty()) {
            return cookies;
        }
        return getDeviceInitCookies(machineId);
    }

    /**
     * @deprecated 使用 {@link #updateDeviceInitCookies(String, List)} 或 {@link #updateUserSessionCookies(String, String, List)} 代替
     */
    @Deprecated
    public void updateSessionCookies(String machineId, List<Cookie> cookies) {
        String userId = getActiveAccount(machineId);
        if (userId != null && hasUserSession(machineId, userId)) {
            updateUserSessionCookies(machineId, userId, cookies);
        } else {
            updateDeviceInitCookies(machineId, cookies);
        }
    }

    /**
     * @deprecated 使用 {@link #getActiveSession(String)} 代替
     */
    @Deprecated
    public boolean isLoggedIn(String machineId) {
        return getActiveSession(machineId) != null;
    }

    /**
     * @deprecated 使用 {@link #removeUserSession(String, String)} 或 {@link #clearDeviceAllData(String)} 代替
     */
    @Deprecated
    public void removeSession(String machineId) {
        String userId = getActiveAccount(machineId);
        if (userId != null) {
            removeUserSession(machineId, userId);
        }
        removeDeviceInitSession(machineId);
    }
}