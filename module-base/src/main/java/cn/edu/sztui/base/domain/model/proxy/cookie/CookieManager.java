package cn.edu.sztui.base.domain.model.proxy.cookie;


import org.apache.http.client.CookieStore;
import org.apache.http.cookie.Cookie;

import java.util.List;

public interface CookieManager {
    CookieStore getOrCreateCookieStore(String userId);
    void clearUserCookies(String userId);
    void addCookies(String userId, List<Cookie> cookies);
    List<Cookie> getUserCookies(String userId);
    Cookie createCookie(String name, String value, String domain, String path);
}
