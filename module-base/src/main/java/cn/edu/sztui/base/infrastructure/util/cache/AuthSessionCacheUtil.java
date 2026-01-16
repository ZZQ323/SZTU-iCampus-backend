package cn.edu.sztui.base.infrastructure.util.cache;

import cn.edu.sztui.base.infrastructure.convertor.CookieConverter;
import cn.edu.sztui.base.infrastructure.util.cache.dto.ProxySession;
import cn.edu.sztui.common.cache.util.CacheUtil;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.alibaba.fastjson2.JSON;
import com.microsoft.playwright.options.Cookie;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

/**
 * 代理会话缓存工具
 * 存储结构：
 * - auth:init:{unionID} -> seesion ，所有的信息，状态全部储存在 proxy
 */
@Slf4j
@Component
public class AuthSessionCacheUtil {

    private static final String MACHINE_SESSION_KEY = "auth:init:";
    private static final String USER_MAPPING_KEY = "auth:user:";

    // 机器会话过期时间：30分钟
    private static final long MACHINE_SESSION_EXPIRE = 1800;
    // 登录会话过期时间：1小时
    private static final long LOGIN_SESSION_EXPIRE = 3600;

    @Resource
    private CacheUtil cacheUtil;

    /**
     * 生成机器ID
     */
    @Deprecated
    public String generateMachineId() {
        return UUID.randomUUID().toString().replace("-", "");
    }

    /**
     * 获取初始会话
     * 登录前，无账号，只有小程序code
     */
    public ProxySession getMachineSession(String code) {
        if (!StringUtils.hasText(code)) return null;
        Object obj = cacheUtil.hget(MACHINE_SESSION_KEY , code);
        if (obj == null) return null;
        return JSON.parseObject(obj.toString(), ProxySession.class);
    }

    /**
     * 保存初始会话
     * 登录前，无账号，只有小程序code
     */
    public void saveInitialSession(String code, List<Cookie> cookies) {
        if (!StringUtils.hasText(code) || CollectionUtils.isEmpty(cookies))return;
        ProxySession session = new ProxySession();
        session.setWxCode(code);
        session.setCookiesJson(CookieConverter.toCookieStrings(cookies));
        // 获取的系统时间？
        session.setCreateTime(System.currentTimeMillis());
        session.setLastUpdateTime(System.currentTimeMillis());

        cacheUtil.hset(MACHINE_SESSION_KEY,code, JSON.toJSONString(session), MACHINE_SESSION_EXPIRE);
        log.info("保存小程序code: {}，session：{}", code, session);
    }

    /**
     * 绑定用户到机器会话（登录成功后）
     */
    public void bindUserToMachine(String code, String userId, List<Cookie> newCookies) {
        ProxySession session = getMachineSession(code);
        // 前端通过每次打开都进行初始化的方式进行检查，这里仅做意外的检测
        if (session == null) {
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "无法获取初始化会话！！！！", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
        session.setUserId(userId);
        session.setCookiesJson(CookieConverter.toCookieStrings(newCookies));
        session.setLastUpdateTime(System.currentTimeMillis());
        session.setLoggedIn(true);

        // 更新机器会话（延长过期时间）
        cacheUtil.hset(MACHINE_SESSION_KEY,code+":"+userId, JSON.toJSONString(session), LOGIN_SESSION_EXPIRE);
        // 创建用户到机器的映射
        cacheUtil.hset(USER_MAPPING_KEY,userId, code, LOGIN_SESSION_EXPIRE);
        log.info("用户 {} 绑定到小程序code {}", userId, code);
    }

    /**
     * 更新会话Cookie，每次context请求玩之后都需要经历这一步
     */
    public void updateSessionCookies(String machineId, List<Cookie> cookies) {
        ProxySession session = getMachineSession(machineId);
        if (session == null) {
            log.warn("机器会话不存在: {}", machineId);
            return;
        }

        session.setCookiesJson(CookieConverter.toCookieStrings(cookies));
        session.setLastUpdateTime(Instant.now().toEpochMilli());

        long expire = session.isLoggedIn() ? LOGIN_SESSION_EXPIRE : MACHINE_SESSION_EXPIRE;
        cacheUtil.hset(MACHINE_SESSION_KEY,machineId, JSON.toJSONString(session), expire);
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
        return CookieConverter.fromCookieDTOs(session.getCookiesJson());
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
}
