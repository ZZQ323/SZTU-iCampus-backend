package cn.edu.sztui.base.infrastructure.util;

import lombok.extern.slf4j.Slf4j;
import org.apache.http.cookie.Cookie;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 反爬虫规避工具
 * 策略：让HTTP请求看起来像真实浏览器行为
 */

@Slf4j
@Component
public class AntiDetectionUtils {

    // 真实浏览器User-Agent池
    private static final List<String> USER_AGENTS = Arrays.asList(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    );

    // Accept-Language 变体
    private static final List<String> ACCEPT_LANGUAGES = Arrays.asList(
            "zh-CN,zh;q=0.9,en;q=0.8",
            "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "zh-CN,zh;q=0.9",
            "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
    );

    /**
     * 获取随机User-Agent
     */
    public String getRandomUserAgent() {
        return USER_AGENTS.get(ThreadLocalRandom.current().nextInt(USER_AGENTS.size()));
    }

    /**
     * 获取随机Accept-Language
     */
    public String getRandomAcceptLanguage() {
        return ACCEPT_LANGUAGES.get(ThreadLocalRandom.current().nextInt(ACCEPT_LANGUAGES.size()));
    }

    /**
     * 获取完整的浏览器请求头
     */
    public Map<String, String> getBrowserHeaders(String referer) {
        Map<String, String> headers = new LinkedHashMap<>();

        headers.put("User-Agent", getRandomUserAgent());
        headers.put("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8");
        headers.put("Accept-Language", getRandomAcceptLanguage());
        headers.put("Accept-Encoding", "gzip, deflate, br");
        headers.put("Connection", "keep-alive");
        headers.put("Upgrade-Insecure-Requests", "1");

        // Sec-Fetch 系列头（现代浏览器特征）
        headers.put("Sec-Fetch-Dest", "document");
        headers.put("Sec-Fetch-Mode", "navigate");
        headers.put("Sec-Fetch-Site", referer != null ? "same-origin" : "none");
        headers.put("Sec-Fetch-User", "?1");

        // 可选：添加Referer
        if (referer != null) {
            headers.put("Referer", referer);
        }

        return headers;
    }

    /**
     * 模拟人类行为的随机延迟（毫秒）
     */
    public void randomDelay() {
        try {
            // 300ms - 1500ms 随机延迟
            long delay = ThreadLocalRandom.current().nextLong(300, 1500);
            Thread.sleep(delay);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /**
     * 快速操作之间的短延迟
     */
    public void shortDelay() {
        try {
            // 100ms - 500ms
            long delay = ThreadLocalRandom.current().nextLong(100, 500);
            Thread.sleep(delay);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /**
     * 验证Cookie是否包含必要字段
     */
    public boolean hasRequiredCookies(List<?> cookies, String... requiredNames) {
        if (cookies == null || cookies.isEmpty()) {
            return false;
        }

        Set<String> cookieNames = new HashSet<>();
        for (Object cookie : cookies) {
            // 适配不同Cookie类型
            if (cookie instanceof Cookie c) {
                cookieNames.add(c.getName());
            }
        }

        for (String required : requiredNames) {
            if (!cookieNames.contains(required)) {
                log.warn("缺少必要Cookie: {}", required);
                return false;
            }
        }
        return true;
    }
}
