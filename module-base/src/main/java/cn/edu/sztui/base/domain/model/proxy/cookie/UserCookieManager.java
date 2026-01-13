package cn.edu.sztui.base.domain.model.proxy.cookie;

import lombok.extern.slf4j.Slf4j;
import org.apache.http.client.CookieStore;
import org.apache.http.cookie.Cookie;
import org.apache.http.impl.client.BasicCookieStore;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.List;

@Slf4j
@Component
public class UserCookieManager implements CookieManager {
    @Override
    public CookieStore getOrCreateCookieStore(String userId) {
        return new BasicCookieStore();
    }

    @Override
    public void clearUserCookies(String userId) {

    }

    @Override
    public void addCookies(String userId, List<Cookie> cookies) {

    }

    @Override
    public List<Cookie> getUserCookies(String userId) {
        return Collections.emptyList();
    }

    @Override
    public Cookie createCookie(String name, String value, String domain, String path) {
        return null;
    }

    public void destroy() {

    }
}
