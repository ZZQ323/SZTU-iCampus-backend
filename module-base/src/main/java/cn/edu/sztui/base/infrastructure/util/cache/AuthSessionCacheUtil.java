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

import java.util.List;
import java.util.Objects;

/**
 * 代理会话缓存工具
 * 存储结构：
 * - auth:init:{unionID} -> seesion ，所有的信息，状态全部储存在 proxy
 */
@Slf4j
@Component
public class AuthSessionCacheUtil {
    private static final String UNIONID_SESSION_KEY = "auth:miniapp:";

    // 机器会话过期时间：30分钟
    private static final long MACHINE_SESSION_EXPIRE = 1800;
    // 登录会话过期时间：1小时
    private static final long LOGIN_SESSION_EXPIRE = 3600;
    @Resource
    private CacheUtil cacheUtil;

    /**
     * 获取会话
     * @param unionID
     * @return
     */
    public ProxySession getSession(String unionID) {
        if ( !StringUtils.hasText(unionID) ) return null;
        Object obj = cacheUtil.hget(UNIONID_SESSION_KEY, unionID);
        if (obj == null) return null;
        return JSON.parseObject(obj.toString(), ProxySession.class);
    }

    /**
     * <p>只更新基础信息</p>
     * <p>登录前，无账号，只有账号在小程序中的 unionID</p>
     *
     * @param unionID
     * @param cookies
     */
    public void saveOrUpdateSession(String unionID, List<Cookie> cookies) {
        ProxySession session = getSession(unionID);
        if (StringUtils.hasText(unionID) && !CollectionUtils.isEmpty(cookies)) {
            if(Objects.isNull(session)){
                session = new ProxySession();
                // 获取的系统时间？
                session.setWxCode(unionID);
                session.setCreateTime(System.currentTimeMillis());
            }
            session.setCookiesJson(CookieConverter.toCookieStrings(cookies));
            session.setLastUpdateTime(System.currentTimeMillis());// 自动覆盖，管理expire
            cacheUtil.hset(UNIONID_SESSION_KEY,unionID, JSON.toJSONString(session), MACHINE_SESSION_EXPIRE);
            log.info("保存小程序unionID: {}，session：{}", unionID, session);
        }
    }

    /**
     * 登录更新登录状态
     * @param unionID
     * @param userId
     * @param newCookies
     */
    public void sessionLoginBind(String unionID, String userId, List<Cookie> newCookies) {
        ProxySession session = getSession(unionID);
        if (session == null) {
            // 前端通过每次打开都进行初始化的方式进行检查，这里仅做意外的检测
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "无法获取初始化会话！！！！", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
        session.setUserId(userId);
        session.setCookiesJson(CookieConverter.toCookieStrings(newCookies));
        session.setLastUpdateTime(System.currentTimeMillis());
        session.setLoggedIn(true);
        // 更新机器会话（延长过期时间）
        cacheUtil.hset(UNIONID_SESSION_KEY,unionID+":"+userId, JSON.toJSONString(session), LOGIN_SESSION_EXPIRE);
        log.info("用户 {} 绑定到小程序unionID {}", userId, unionID);
    }

    /**
     * 检查机器会话是否有效
     * @param unionID
     * @return
     */
    public boolean hasSession(String unionID) {
        return cacheUtil.hHasKey(UNIONID_SESSION_KEY, unionID);
    }

    /**
     * 检查是否已登录
     * @param unionID
     * @return
     */
    public boolean isLoggedIn(String unionID) {
        ProxySession session = getSession(unionID);
        return !Objects.isNull(session) && session.isLoggedIn();
    }

    /**
     * 删除会话（登出）
     */
    @Deprecated
    public void sessionLogoutBind(String unionID) {
        ProxySession session = getSession(unionID);
        if (session != null && StringUtils.hasText(session.getUserId())) {
            cacheUtil.del(UNIONID_SESSION_KEY + session.getUserId());
        }
        cacheUtil.del(UNIONID_SESSION_KEY + unionID);
        log.info("删除机器会话: {}", unionID);
    }

    /**
     * 通过用户ID删除会话
     */
    @Deprecated
    public void removeSessionByUserId(String userId) {
        Object machineIdObj = cacheUtil.hget (UNIONID_SESSION_KEY , userId);
        if (machineIdObj != null) {
            sessionLogoutBind(machineIdObj.toString());
        }
        cacheUtil.del(UNIONID_SESSION_KEY + userId);
    }
}
