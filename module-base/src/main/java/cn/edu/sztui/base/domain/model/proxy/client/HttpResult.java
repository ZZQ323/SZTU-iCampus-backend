package cn.edu.sztui.base.domain.model.proxy.client;

import lombok.Builder;
import lombok.Data;
import lombok.experimental.Accessors;
import org.apache.http.cookie.Cookie;

import java.util.List;
import java.util.Map;

@Data
@Accessors(chain = true)
@Builder
public class HttpResult {
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
