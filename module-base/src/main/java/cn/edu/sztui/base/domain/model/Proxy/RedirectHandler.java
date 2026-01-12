package cn.edu.sztui.base.domain.model.Proxy;

import org.apache.hc.client5.http.cookie.Cookie;
import org.apache.hc.client5.http.cookie.CookieStore;
import org.apache.hc.client5.http.protocol.HttpClientContext;

import java.util.*;

public class RedirectHandler {
    private final CookieStore cookieStore;
    private final List<Cookie> allCookies = new ArrayList<>();

    public RedirectHandler(CookieStore cookieStore) {
        this.cookieStore = cookieStore;
    }

    public void processCookies(HttpClientContext context) {
        List<Cookie> currentCookies = context.getCookieStore().getCookies();

        // 使用 Map 去重，提高性能
        Map<String, Cookie> cookieMap = new HashMap<>();

        // 添加已有Cookie
        allCookies.forEach(c ->
                cookieMap.put(getCookieKey(c), c));

        // 更新/添加新Cookie
        currentCookies.forEach(c -> {
            cookieStore.addCookie(c);
            cookieMap.put(getCookieKey(c), c);
        });

        allCookies.clear();
        allCookies.addAll(cookieMap.values());
    }

    private String getCookieKey(Cookie cookie) {
        return cookie.getName() + "@" + (cookie.getDomain() == null ? "" : cookie.getDomain());
    }

    public List<Cookie> getAllCookies() {
        return Collections.unmodifiableList(allCookies);
    }
}
