package cn.edu.sztui.base.domain.model.proxy;

import cn.edu.sztui.base.domain.model.proxy.client.HttpClientFactory;
import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import cn.edu.sztui.base.domain.model.proxy.cookie.CookieManager;
import cn.edu.sztui.base.domain.model.proxy.header.BrowserHeaderBuilder;
import cn.edu.sztui.base.domain.model.proxy.parser.CookieParser;
import cn.edu.sztui.base.domain.model.proxy.redirect.HtmlRedirectHandler;
import cn.edu.sztui.base.domain.model.proxy.redirect.HttpRedirectHandler;
import cn.edu.sztui.base.domain.model.proxy.redirect.JsRedirectHandler;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.annotation.Resource;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.Header;
import org.apache.http.NameValuePair;
import org.apache.http.ParseException;
import org.apache.http.client.CookieStore;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.cookie.Cookie;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.cookie.BasicClientCookie;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * 学校网站HTTP客户端 - 重构后的门面类
 * 职责：协调各组件完成HTTP请求
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class SchoolHttpClient {

    @Resource
    private final HttpClientFactory clientFactory;
    @Resource
    private final CookieManager cookieManager;
    @Resource
    private final BrowserHeaderBuilder headerBuilder;
    @Resource
    private final CookieParser cookieParser;
    @Resource
    private final HttpRedirectHandler httpRedirectHandler;
    @Resource
    private final JsRedirectHandler jsRedirectHandler;
    @Resource
    private final HtmlRedirectHandler htmlRedirectHandler;

    private CloseableHttpClient httpClient;

    @PostConstruct
    public void init() throws Exception {
        httpClient = clientFactory.createDefaultClient();
        log.info("SchoolHttpClient 初始化完成");
    }

    // ==================== 委托给 CookieManager ====================

    public CookieStore getOrCreateCookieStore(String userId) {
        return cookieManager.getOrCreateCookieStore(userId);
    }

    public void clearUserCookies(String userId) {
        cookieManager.clearUserCookies(userId);
    }

    public void addCookies(String userId, List<Cookie> cookies) {
        cookieManager.addCookies(userId, cookies);
    }

    public List<Cookie> getUserCookies(String userId) {
        return cookieManager.getUserCookies(userId);
    }

    // ==================== HTTP 请求方法 ====================

    public HttpResult doGet(String userId, String url) throws IOException {
        CookieStore cookieStore = cookieManager.getOrCreateCookieStore(userId);
        HttpClientContext context = createContext(cookieStore);

        HttpGet httpGet = new HttpGet(url);
        headerBuilder.addBrowserHeaders(httpGet);

        try (CloseableHttpResponse response = httpClient.execute(httpGet, context)) {
            return buildResult(response, context);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
    }

    public HttpResult doPost(String userId, String url, Map<String, String> formData) throws IOException {
        CookieStore cookieStore = cookieManager.getOrCreateCookieStore(userId);
        HttpClientContext context = createContext(cookieStore);

        HttpPost httpPost = new HttpPost(url);
        headerBuilder.addBrowserHeaders(httpPost);
        httpPost.setHeader("Content-Type", "application/x-www-form-urlencoded;charset=UTF-8");

        List<NameValuePair> params = new ArrayList<>();
        formData.forEach((k, v) -> params.add(new BasicNameValuePair(k, v)));
        httpPost.setEntity(new UrlEncodedFormEntity(params, StandardCharsets.UTF_8));

        try (CloseableHttpResponse response = httpClient.execute(httpPost, context)) {
            return buildResult(response, context);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
    }

    public HttpResult doGetWithManualRedirect(String machineId, String url, int maxRedirects) throws Exception {
        // TODO 补全cookie的初始化过程，合理分配 manager和 cacheutil 的工作
        CookieStore cookieStore = cookieManager.getOrCreateCookieStore(machineId);
        List<Cookie> allCookies = new ArrayList<>();
        try (CloseableHttpClient client = clientFactory.createNoRedirectClient()) {
            String currentUrl = url;
            HttpResult lastResult = null;

            for (int i = 0; i < maxRedirects; i++) {
                HttpClientContext context = createContext(cookieStore);
                HttpGet httpGet = new HttpGet(currentUrl);
                headerBuilder.addBrowserHeaders(httpGet);

                if (lastResult != null && lastResult.getFinalUrl() != null) {
                    headerBuilder.addReferer(httpGet, lastResult.getFinalUrl());
                }
                // 执行请求
                try ( CloseableHttpResponse response = client.execute(httpGet, context) ) {
                    lastResult = buildResult(response, context);
                    lastResult.setFinalUrl(currentUrl);

                    // TODO 合并去重 Cookie，覆写重复的部分
                    collectCookies(lastResult.getCookies(), allCookies, cookieStore);

                    // 尝试文档重定向
                    Optional<String> htmlRedirect = htmlRedirectHandler.extractRedirectUrl(lastResult, currentUrl);
                    if (htmlRedirect.isPresent() && !htmlRedirect.get().equals(lastResult.getFinalUrl()) ) {
                        currentUrl = htmlRedirect.get();
                        log.info("HTTP重定向 {} -> {}", i + 1, currentUrl);
                        continue;
                    }

                    // 尝试 HTTP头 重定向
                    Optional<String> httpRedirect = httpRedirectHandler.extractRedirectUrl(lastResult, currentUrl);
                    if (httpRedirect.isPresent()  && !httpRedirect.get().equals(lastResult.getFinalUrl()) ) {
                        currentUrl = httpRedirect.get();
                        log.info("HTTP重定向 {} -> {}", i + 1, currentUrl);
                        continue;
                    }

                    // 尝试 JS 重定向
                    Optional<String> jsRedirect = jsRedirectHandler.extractRedirectUrl(lastResult, currentUrl);
                    if (jsRedirect.isPresent()  && !jsRedirect.get().equals(lastResult.getFinalUrl()) ) {
                        currentUrl = jsRedirect.get();
                        log.debug("JS重定向 {} -> {}", i + 1, currentUrl);
                        continue;
                    }

                    break;
                }
            }

            if (lastResult != null) {
                lastResult.setCookies(allCookies);
            }
            return lastResult;
        }
    }

    public HttpResult doPostWithManualRedirect(String machineId, String url, int maxRedirects, Map<String, String> formData) throws Exception {
        CookieStore cookieStore = cookieManager.getOrCreateCookieStore(machineId);
        return null;
    }

    // ==================== 私有辅助方法 ====================

    private HttpClientContext createContext(CookieStore cookieStore) {
        HttpClientContext context = HttpClientContext.create();
        context.setCookieStore(cookieStore);
        return context;
    }


    private HttpResult buildResult(CloseableHttpResponse response, HttpClientContext context)
            throws IOException, ParseException {
        List<Cookie> cookies = new ArrayList<>();
        for (Header header : response.getHeaders("Set-Cookie")) {
            Cookie cookie = parseSetCookieHeader(header.getValue());
            if (cookie != null)
                cookies.add(cookie);
        }
        Map<String, String> headers = new HashMap<>();
        for (Header header : response.getAllHeaders())headers.put(header.getName(), header.getValue());
        return HttpResult.builder()
            .statusCode(response.getStatusLine().getStatusCode())
            .body(EntityUtils.toString(response.getEntity(), StandardCharsets.UTF_8))
            .cookies(cookies)
            .headers(headers)
            .build();
    }

    /**
     * 解析 Set-Cookie header 为 Cookie 对象
     */
    private Cookie parseSetCookieHeader(String headerValue){
        if (headerValue == null || headerValue.isEmpty()) return null;
        String[] parts = headerValue.split(";");
        String[] nameValue = parts[0].trim().split("=", 2);
        if (nameValue.length < 2) return null;
        BasicClientCookie cookie = new BasicClientCookie(nameValue[0].trim(), nameValue[1].trim());
        // 解析属性
        for (int i = 1; i < parts.length; i++) {
            String part = parts[i].trim();
            String[] attr = part.split("=", 2);
            String attrName = attr[0].trim().toLowerCase();
            String attrValue = attr.length > 1 ? attr[1].trim() : "";
            switch (attrName) {
                case "domain":cookie.setDomain(attrValue);break;
                case "path":cookie.setPath(attrValue); break;
                case "secure":cookie.setSecure(true);break;
                case "httponly":cookie.setAttribute("httponly", "true");break;
                // max-age / expires 可按需添加
            }
        }
        return cookie;
    }

    private void collectCookies(List<Cookie> newCookies, List<Cookie> allCookies, CookieStore store) {
        for (Cookie cookie : newCookies) {
            allCookies.removeIf(c -> c.getName().equals(cookie.getName())
                    && Objects.equals(c.getDomain(), cookie.getDomain()));
            allCookies.add(cookie);
            store.addCookie(cookie);
        }
    }

    @PreDestroy
    public void destroy() throws IOException {
        if (httpClient != null) {
            httpClient.close();
        }
        log.info("SchoolHttpClient 已销毁");
    }
}
