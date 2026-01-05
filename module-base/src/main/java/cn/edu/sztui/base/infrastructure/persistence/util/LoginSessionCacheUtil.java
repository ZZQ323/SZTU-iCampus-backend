package cn.edu.sztui.base.infrastructure.persistence.util;

import cn.edu.sztui.common.cache.util.CacheUtil;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.options.Cookie;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;
import java.util.List;

@Slf4j
@Component
public class LoginSessionCacheUtil {
    private static final String LOGIN_SESSION_KEY = "login:session";
    private static final long SESSION_EXPIRE_SECONDS = 1800; // 半个小时过期

    @Resource
    private CacheUtil cacheUtil;

    /**
     * 保存登录 cookies
     *
     * @param studentId 学号
     * @param cookies   Playwright 返回的 cookies
     */
    public void saveCookies(String studentId, List<Cookie> cookies) {
        if (StringUtils.isEmpty(studentId) || CollectionUtils.isEmpty(cookies)) {
            return;
        }
        String cookieJson = JSONObject.toJSONString(cookies);
        cacheUtil.hset(LOGIN_SESSION_KEY, studentId, cookieJson, SESSION_EXPIRE_SECONDS);
        log.info("已缓存用户{}的cookies", studentId);
    }

    /**
     * 获取登录 cookies
     *
     * @param studentId 学号
     * @return cookies 列表，不存在返回 null
     */
    public List<Cookie> getCookies(String studentId) {
        if (StringUtils.isEmpty(studentId)) {
            return null;
        }
        Object obj = cacheUtil.hget(LOGIN_SESSION_KEY, studentId);
        if (obj == null) {
            return null;
        }
        return JSONArray.parseArray(obj.toString(), Cookie.class);
    }

    /**
     * 检查是否存在有效的登录缓存
     */
    public boolean hasValidSession(String studentId) {
        return cacheUtil.hHasKey(LOGIN_SESSION_KEY, studentId);
    }

    /**
     * 删除登录缓存（登出或 cookie 失效时调用）
     */
    public void removeCookies(String studentId) {
        cacheUtil.hdel(LOGIN_SESSION_KEY, studentId);
        log.info("已删除用户{}的cookies缓存", studentId);
    }

    /**
     * 将缓存的 cookies 应用到 BrowserContext
     */
    public void applyCookiesToContext(String studentId, BrowserContext context, String url) {
        List<Cookie> cookies = getCookies(studentId);
        if (!CollectionUtils.isEmpty(cookies)) {
            context.addCookies(cookies);
            log.info("已将缓存cookies应用到context, 用户: {}", studentId);
        }
    }
}
