package cn.edu.sztui.base.domain.model.Proxy;

import lombok.extern.slf4j.Slf4j;
import org.apache.hc.client5.http.classic.methods.HttpGet;
import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.config.RequestConfig;
import org.apache.hc.client5.http.cookie.BasicCookieStore;
import org.apache.hc.client5.http.cookie.Cookie;
import org.apache.hc.client5.http.cookie.CookieStore;
import org.apache.hc.client5.http.entity.UrlEncodedFormEntity;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.client5.http.impl.cookie.BasicClientCookie;
import org.apache.hc.client5.http.protocol.HttpClientContext;
import org.apache.hc.core5.http.ClassicHttpResponse;
import org.apache.hc.core5.http.Header;
import org.apache.hc.core5.http.NameValuePair;
import org.apache.hc.core5.http.ParseException;
import org.apache.hc.core5.http.io.entity.EntityUtils;
import org.apache.hc.core5.http.message.BasicNameValuePair;
import org.springframework.stereotype.Component;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.IOException;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
/**
 * 学校网站HTTP客户端
 *
 * 核心功能：
 * 1. 自动处理重定向链（OAuth2流程）
 * 2. 自动管理Cookie（每用户独立CookieStore）
 * 3. 模拟真实浏览器请求头
 */
@Slf4j
@Component
public class SchoolHttpClient {

    private CloseableHttpClient httpClient;

    // 用户ID -> CookieStore 映射，实现会话隔离
    private final ConcurrentHashMap<String, CookieStore> userCookieStores = new ConcurrentHashMap<>();

    // 模拟真实浏览器的UA
    private static final String USER_AGENT =
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

    // 学校网站域名（根据你的实际情况修改）
    private static final String SCHOOL_DOMAIN = "your-school.edu.cn";

    @PostConstruct
    public void init() {
        RequestConfig requestConfig = RequestConfig.custom()
                .setConnectTimeout(30, TimeUnit.SECONDS)
                .setResponseTimeout(30, TimeUnit.SECONDS)
                .setRedirectsEnabled(true)  // 启用自动重定向
                .setMaxRedirects(10)        // 最大重定向次数
                .setCircularRedirectsAllowed(false)
                .build();

        httpClient = HttpClients.custom()
                .setDefaultRequestConfig(requestConfig)
                // 不设置全局CookieStore，每个请求使用独立的Context
                .disableCookieManagement()  // 我们手动管理Cookie
                .build();

        log.info("SchoolHttpClient 初始化完成");
    }

    /**
     * 获取或创建用户的CookieStore
     */
    public CookieStore getOrCreateCookieStore(String userId) {
        return userCookieStores.computeIfAbsent(userId, k -> new BasicCookieStore());
    }

    /**
     * 清除用户Cookie
     */
    public void clearUserCookies(String userId) {
        CookieStore store = userCookieStores.get(userId);
        if (store != null) {
            store.clear();
        }
    }

    /**
     * 保存外部Cookie到用户会话
     */
    public void addCookies(String userId, List<Cookie> cookies) {
        CookieStore store = getOrCreateCookieStore(userId);
        for (Cookie cookie : cookies) {
            store.addCookie(cookie);
        }
    }

    /**
     * 获取用户当前的Cookies
     */
    public List<Cookie> getUserCookies(String userId) {
        CookieStore store = userCookieStores.get(userId);
        return store != null ? store.getCookies() : Collections.emptyList();
    }

    /**
     * 核心方法：发起GET请求，自动处理重定向和Cookie
     *
     * @param userId 用户ID（用于会话隔离）
     * @param url    请求URL
     * @return 响应结果
     */
    public HttpResult doGet(String userId, String url) throws IOException {
        CookieStore cookieStore = getOrCreateCookieStore(userId);
        HttpClientContext context = createContext(cookieStore);

        HttpGet httpGet = new HttpGet(url);
        addBrowserHeaders(httpGet);

        try (ClassicHttpResponse response = httpClient.executeOpen(null, httpGet, context)) {
            return buildResult(response, context);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * 核心方法：发起POST请求（用于登录等）
     */
    public HttpResult doPost(String userId, String url, Map<String, String> formData) throws IOException {
        CookieStore cookieStore = getOrCreateCookieStore(userId);
        HttpClientContext context = createContext(cookieStore);

        HttpPost httpPost = new HttpPost(url);
        addBrowserHeaders(httpPost);
        httpPost.setHeader("Content-Type", "application/x-www-form-urlencoded");

        // 构建表单数据
        List<NameValuePair> params = new ArrayList<>();
        formData.forEach((k, v) -> params.add(new BasicNameValuePair(k, v)));
        httpPost.setEntity(new UrlEncodedFormEntity(params, StandardCharsets.UTF_8));

        try (ClassicHttpResponse response = httpClient.executeOpen(null, httpPost, context)) {
            return buildResult(response, context);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * 手动处理重定向（当需要精细控制时使用）
     * 某些OAuth2流程需要在重定向过程中提取参数
     */
    public HttpResult doGetWithManualRedirect(String userId, String url, int maxRedirects) throws IOException {
        CookieStore cookieStore = getOrCreateCookieStore(userId);

        // 创建不自动重定向的配置
        RequestConfig noRedirectConfig = RequestConfig.custom()
                .setRedirectsEnabled(false)
                .build();

        String currentUrl = url;
        HttpResult lastResult = null;

        for (int i = 0; i < maxRedirects; i++) {
            HttpClientContext context = createContext(cookieStore);
            HttpGet httpGet = new HttpGet(currentUrl);
            httpGet.setConfig(noRedirectConfig);
            addBrowserHeaders(httpGet);

            // 设置Referer（重要：有些网站会检查）
            if (lastResult != null) {
                httpGet.setHeader("Referer", lastResult.getFinalUrl());
            }

            try (ClassicHttpResponse response = httpClient.executeOpen(null, httpGet, context)) {
                lastResult = buildResult(response, context);
                lastResult.setFinalUrl(currentUrl);

                int statusCode = response.getCode();

                // 检查是否是重定向
                if (statusCode >= 300 && statusCode < 400) {
                    Header locationHeader = response.getFirstHeader("Location");
                    if (locationHeader != null) {
                        String location = locationHeader.getValue();
                        // 处理相对路径
                        currentUrl = resolveUrl(currentUrl, location);
                        log.debug("重定向 {} -> {}", i + 1, currentUrl);
                        continue;
                    }
                }
                // 不是重定向或没有Location，返回结果
                break;
            } catch (ParseException e) {
                throw new RuntimeException(e);
            }
        }

        return lastResult;
    }

    /**
     * 创建请求上下文
     */
    private HttpClientContext createContext(CookieStore cookieStore) {
        HttpClientContext context = HttpClientContext.create();
        context.setCookieStore(cookieStore);
        return context;
    }

    /**
     * 添加浏览器请求头（防止被识别为机器人）
     */
    private void addBrowserHeaders(org.apache.hc.core5.http.HttpRequest request) {
        request.setHeader("User-Agent", USER_AGENT);
        request.setHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8");
        request.setHeader("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8");
        request.setHeader("Accept-Encoding", "gzip, deflate, br");
        request.setHeader("Connection", "keep-alive");
        request.setHeader("Upgrade-Insecure-Requests", "1");
        request.setHeader("Sec-Fetch-Dest", "document");
        request.setHeader("Sec-Fetch-Mode", "navigate");
        request.setHeader("Sec-Fetch-Site", "same-origin");
        request.setHeader("Sec-Fetch-User", "?1");
        // 随机化一些可追踪的头
        request.setHeader("Cache-Control", "max-age=0");
    }

    /**
     * 构建响应结果
     */
    private HttpResult buildResult(ClassicHttpResponse response, HttpClientContext context) throws IOException, ParseException {
        HttpResult result = new HttpResult();
        result.setStatusCode(response.getCode());
        result.setBody(EntityUtils.toString(response.getEntity(), StandardCharsets.UTF_8));
        result.setCookies(new ArrayList<>(context.getCookieStore().getCookies()));

        // 获取最终URL（经过重定向后的）
        if (context.getRedirectLocations() != null && !context.getRedirectLocations().contains(URI.create("")) ) {
            result.setFinalUrl(context.getRedirectLocations()
                    .get(context.getRedirectLocations().size() - 1).toString());
        }

        // 提取响应头
        Map<String, String> headers = new HashMap<>();
        for (Header header : response.getHeaders()) {
            headers.put(header.getName(), header.getValue());
        }
        result.setHeaders(headers);

        return result;
    }

    /**
     * URL解析（处理相对路径）
     */
    private String resolveUrl(String baseUrl, String location) {
        if (location.startsWith("http://") || location.startsWith("https://")) {
            return location;
        }
        try {
            java.net.URI base = new java.net.URI(baseUrl);
            return base.resolve(location).toString();
        } catch (Exception e) {
            return location;
        }
    }

    /**
     * 创建Cookie对象（用于手动设置Cookie）
     */
    public BasicClientCookie createCookie(String name, String value, String domain, String path) {
        BasicClientCookie cookie = new BasicClientCookie(name, value);
        cookie.setDomain(domain);
        cookie.setPath(path);
        return cookie;
    }

    @PreDestroy
    public void destroy() throws IOException {
        if (httpClient != null) {
            httpClient.close();
        }
        userCookieStores.clear();
        log.info("SchoolHttpClient 已销毁");
    }

    /**
     * HTTP响应结果封装
     */
    @lombok.Data
    public static class HttpResult {
        private int statusCode;
        private String body;
        private String finalUrl;
        private List<Cookie> cookies;
        private Map<String, String> headers;

        public boolean isSuccess() {
            return statusCode >= 200 && statusCode < 300;
        }

        public boolean isRedirect() {
            return statusCode >= 300 && statusCode < 400;
        }
    }
}
