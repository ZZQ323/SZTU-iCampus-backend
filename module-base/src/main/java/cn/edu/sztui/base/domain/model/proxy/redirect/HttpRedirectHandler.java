package cn.edu.sztui.base.domain.model.proxy.redirect;

import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Slf4j
@Service
public class HttpRedirectHandler implements RedirectHandler {

    @Override
    public Optional<String> extractRedirectUrl(HttpResult result, String currentUrl) {
        if (!result.isRedirect()) {return Optional.empty();}
        String location = result.getHeaders().get("Location");
        if (location == null) {return Optional.empty();}
        int statusCode = result.getStatusCode();
        String resolvedUrl=null;
        if (statusCode >= 300 && statusCode < 400) {
            resolvedUrl = result.getFinalUrl();
        }
        log.info("HTTP重定向: {} -> {}", currentUrl, resolvedUrl);
        return Optional.of(resolvedUrl);
    }

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
}
