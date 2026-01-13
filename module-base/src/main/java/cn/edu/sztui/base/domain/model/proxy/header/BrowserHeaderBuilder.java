package cn.edu.sztui.base.domain.model.proxy.header;

import org.apache.http.HttpRequest;
import org.springframework.stereotype.Component;

@Component
public class BrowserHeaderBuilder {

    private static final String USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0";

    public void addBrowserHeaders(HttpRequest request) {
        request.setHeader("User-Agent", USER_AGENT);
        request.setHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8");
        request.setHeader("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8");
        request.setHeader("Accept-Encoding", "gzip, deflate, br");
        request.setHeader("Connection", "keep-alive");
        request.setHeader("Upgrade-Insecure-Requests", "1");
        request.setHeader("Sec-Fetch-Dest", "empty");
         request.setHeader("Sec-Fetch-Mode", "navigate");
        request.setHeader("Sec-Fetch-Site", "same-origin");
        request.setHeader("Sec-Fetch-User", "?1");
    }

    public void addReferer(HttpRequest request, String referer) {
        if (referer != null) {
            request.setHeader("Referer", referer);
        }
    }
}