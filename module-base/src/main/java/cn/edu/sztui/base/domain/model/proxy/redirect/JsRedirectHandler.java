package cn.edu.sztui.base.domain.model.proxy.redirect;

import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
@Service
public class JsRedirectHandler implements RedirectHandler {

    private static final Pattern G_LINES_PATTERN =
            Pattern.compile("g_lines\\s*=\\s*\\[\\{[^}]*url\\s*:\\s*\"(https?://[^\"]+)\"[^}]*}\\]\\s*;");

    private static final Pattern WINDOW_LOCATION_PATTERN =
            Pattern.compile("window\\.location\\.href\\s*=\\s*[\"'](https?://[^\"']+)[\"']");

    @Override
    public Optional<String> extractRedirectUrl(HttpResult result, String currentUrl) {
        String body = result.getBody();
        if (body == null) {
            return Optional.empty();
        }

        // 优先匹配 g_lines
        String url = extractByPattern(body, G_LINES_PATTERN);
        if (url != null) {
            log.info("提取到JS重定向URL (g_lines): {}", url);
            return Optional.of(url);
        }

        // 备用：匹配 window.location.href
        url = extractByPattern(body, WINDOW_LOCATION_PATTERN);
        if (url != null) {
            log.info("提取到JS重定向URL (location): {}", url);
            return Optional.of(url);
        }

        return Optional.empty();
    }

    private String extractByPattern(String html, Pattern pattern) {
        Matcher matcher = pattern.matcher(html);
        String lastUrl = null;
        while (matcher.find()) {
            lastUrl = matcher.group(1);
        }
        return lastUrl;
    }
}