package cn.edu.sztui.base.domain.model.proxy.redirect;

import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
@Service
public class HtmlRedirectHandler  implements RedirectHandler {

    // <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    //  <html><head>
    //  <title>302 Found</title>
    //  </head><body>
    //  <h1>Found</h1>
    //  <p>The document has moved <a href="https://home-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/bmportal">here</a>.</p>
    //  </body></html>
    @Override
    public Optional<String> extractRedirectUrl(HttpResult result, String currentUrl) {
        String html = result.getBody();
        if (html == null || html.isEmpty()) return Optional.empty();
        // 正则表达式匹配 <a href="...">
        Pattern pattern = Pattern.compile("<a\\s+href\\s*=\\s*[\"']([^\"']+)[\"'][^>]*>", Pattern.CASE_INSENSITIVE);
        Matcher matcher = pattern.matcher(html);

        if (matcher.find()) {
            String redirectUrl = matcher.group(1);
            // 处理相对路径
            if (!redirectUrl.startsWith("http://") && !redirectUrl.startsWith("https://"))
                redirectUrl = resolveRelativeUrl(currentUrl, redirectUrl);
            return Optional.of(redirectUrl);
        }
        return Optional.empty();
    }

    private String resolveRelativeUrl(String baseUrl, String relativePath) {
        try {
            // 使用 URL 类解析相对路径
            java.net.URL base = new java.net.URL(baseUrl);
            return new java.net.URL(base, relativePath).toString();
        } catch (Exception e) {
            // 如果无法解析，返回原始相对路径
            return relativePath;
        }
    }
}
