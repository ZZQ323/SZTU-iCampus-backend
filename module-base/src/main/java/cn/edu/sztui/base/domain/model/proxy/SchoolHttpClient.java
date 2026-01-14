package cn.edu.sztui.base.domain.model.proxy;

import cn.edu.sztui.base.domain.model.proxy.client.HttpClientFactory;
import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import cn.edu.sztui.base.domain.model.proxy.header.BrowserHeaderBuilder;
import cn.edu.sztui.base.domain.model.proxy.redirect.HtmlRedirectHandler;
import cn.edu.sztui.base.domain.model.proxy.redirect.HttpRedirectHandler;
import cn.edu.sztui.base.domain.model.proxy.redirect.JsRedirectHandler;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
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
import org.apache.http.impl.client.BasicCookieStore;
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
    private final BrowserHeaderBuilder headerBuilder;
    @Resource
    private final HttpRedirectHandler httpRedirectHandler;
    @Resource
    private final JsRedirectHandler jsRedirectHandler;
    @Resource
    private final HtmlRedirectHandler htmlRedirectHandler;
    @Resource
    private ProxySessionCacheUtil  proxySessionCacheUtil;

    private CloseableHttpClient httpClient;

    @PostConstruct
    public void init() throws Exception {
        httpClient = clientFactory.createDefaultClient();
        log.info("SchoolHttpClient 初始化完成");
    }

    @PreDestroy
    public void destroy() throws IOException {
        if (httpClient != null) {
            httpClient.close();
        }
        log.info("SchoolHttpClient 已销毁");
    }

    // ==================== HTTP 请求方法 ====================

    public HttpResult doGet(String machineId,String userId, String url) throws Exception {
        if(!proxySessionCacheUtil.hasUserSession(machineId,userId)){
            return HttpResult.builder()
                    .statusCode(403)
                    .body("请重新初始化！！")
                    .build();
        }
        List<Cookie> cookies = proxySessionCacheUtil.getDeviceInitCookies(machineId);
        // List<Cookie> → CookieStore
        BasicCookieStore cookieStore = new BasicCookieStore();
        for (Cookie cookie : cookies) {
            cookieStore.addCookie(cookie);
        }
        HttpClientContext context = createContext(cookieStore);

        HttpGet httpGet = new HttpGet(url);
        headerBuilder.addBrowserHeaders(httpGet);
        try (CloseableHttpResponse response = httpClient.execute(httpGet, context)) {
            return buildResult(response, context);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
    }

    public HttpResult doPost(String machineId,String url, Map<String, String> formData,List<Cookie> oldCookies) throws Exception {
        if(!proxySessionCacheUtil.hasDeviceInitSession(machineId)){
            return HttpResult.builder()
                    .statusCode(403)
                    .body("请重新初始化！！")
                    .build();
        }
        List<Cookie> cookies = proxySessionCacheUtil.getDeviceInitCookies(machineId);
        // List<Cookie> → CookieStore
        BasicCookieStore cookieStore = new BasicCookieStore();
        for (Cookie cookie : cookies) {
            cookieStore.addCookie(cookie);
        }
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

    public HttpResult doPost(String machineId,String userId, String url, Map<String, String> formData,List<Cookie> oldCookies) throws Exception {
        if(!proxySessionCacheUtil.hasUserSession(machineId,userId)){
            return HttpResult.builder()
                    .statusCode(403)
                    .body("请重新初始化！！")
                    .build();
        }
        List<Cookie> cookies = proxySessionCacheUtil.getDeviceInitCookies(machineId);
        // List<Cookie> → CookieStore
        BasicCookieStore cookieStore = new BasicCookieStore();
        for (Cookie cookie : cookies) {
            cookieStore.addCookie(cookie);
        }
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

    // 没有成功登录过，所以只有 machineId
    public HttpResult doGetWithManualRedirect(String machineId, String url, int maxRedirects,List<Cookie> oldCookies) throws Exception {
        List<Cookie> allCookies;
        if(Objects.isNull(oldCookies) || oldCookies.isEmpty()){
            allCookies = new ArrayList<>();
        }else{
            allCookies = new ArrayList<>(oldCookies);
        }
        try (CloseableHttpClient client = clientFactory.createNoRedirectClient()) {
            String currentUrl = url;
            HttpResult lastResult = null;
            HttpClientContext context = null;
            BasicCookieStore cookieStore = null;

            for (int i = 0; i < maxRedirects; i++) {
                // 根据 cookie 进行 context 创建，所以只需要更新 allCookies 就行
                cookieStore = new BasicCookieStore();
                for (Cookie cookie : allCookies) cookieStore.addCookie(cookie);
                context = createContext(cookieStore);
                HttpGet httpGet = new HttpGet(currentUrl);
                headerBuilder.addBrowserHeaders(httpGet);

                if (lastResult != null && lastResult.getFinalUrl() != null)
                    headerBuilder.addReferer(httpGet, lastResult.getFinalUrl());

                // 执行请求
                try ( CloseableHttpResponse response = client.execute(httpGet, context) ) {
                    lastResult = buildResult(response, context);
                    lastResult.setFinalUrl(currentUrl);

                    // 合并去重 Cookie，覆写重复的部分
                    for (Cookie cookie : lastResult.getCookies()) {
                        // allCookies.removeIf(c -> c.getName().equals(cookie.getName()) && Objects.equals(c.getDomain(), cookie.getDomain()));
                        // 同名则替换，因为域名在网关会一直跳转
                        allCookies.removeIf( c -> c.getName().equals(cookie.getName()) );
                        allCookies.add(cookie);
                    }

                    // 不盲目相信 statusCode
                    // 尝试文档重定向
                    Optional<String> htmlRedirect = htmlRedirectHandler.extractRedirectUrl(lastResult, currentUrl);
                    if (htmlRedirect.isPresent() && !htmlRedirect.get().equals(lastResult.getFinalUrl()) ) {
                        currentUrl = htmlRedirect.get();
                        log.info("HTTP重定向 {} -> {}", i + 1, currentUrl);
                        continue;
                    }

                    // 尝试 HTTP header 的 Location 重定向
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
                        log.info("JS重定向 {} -> {}", i + 1, currentUrl);
                        continue;
                    }
                    break;
                }
            }
            // 返回更新一次 cookie
            if (lastResult != null) lastResult.setCookies(allCookies);
            return lastResult;
        }
    }

    // TODO 以登录功能为例子进行完善
    public HttpResult doPostWithManualRedirect(String machineId, String url, int maxRedirects, Map<String, String> formData,List<Cookie> oldCookies) throws Exception {

        return null;
    }

    // ==================== 私有辅助方法 ====================

    private HttpClientContext createContext(CookieStore cookieStore) {
        HttpClientContext context = HttpClientContext.create();
        context.setCookieStore(cookieStore);
        return context;
    }

    /**
     * 解析返回的结果
     * @param response
     * @param context
     * @return
     * @throws IOException
     * @throws ParseException
     */
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

    // HACK： 手撕 String header 转 cookie，因为貌似没有直接转换的方法
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

    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Cookie 列表 → JSON 字符串（存储用）
     */
    @Deprecated
    public String cookiesToJson(List<Cookie> cookies) throws Exception {
        List<Map<String, String>> list = new ArrayList<>();
        for (Cookie cookie : cookies) {
            Map<String, String> map = new HashMap<>();
            map.put("name", cookie.getName());
            map.put("value", cookie.getValue());
            map.put("domain", cookie.getDomain());
            map.put("path", cookie.getPath());
            map.put("secure", String.valueOf(cookie.isSecure()));
            list.add(map);
        }
        return objectMapper.writeValueAsString(list);
    }

    /**
     * JSON 字符串 → CookieStore（读取用）
     */
    @Deprecated
    public CookieStore jsonToCookieStore(String json) throws Exception {
        BasicCookieStore cookieStore = new BasicCookieStore();
        if (json == null || json.isEmpty()) return cookieStore;
        List<Map<String, String>> list = objectMapper.readValue(json,new TypeReference<List<Map<String, String>>>() {});
        for (Map<String, String> map : list) {
            BasicClientCookie cookie = new BasicClientCookie(map.get("name"), map.get("value"));
            cookie.setDomain(map.get("domain"));
            cookie.setPath(map.get("path"));
            cookie.setSecure(Boolean.parseBoolean(map.get("secure")));
            cookieStore.addCookie(cookie);
        }
        return cookieStore;
    }

}
