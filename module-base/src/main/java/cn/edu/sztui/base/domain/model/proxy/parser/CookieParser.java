package cn.edu.sztui.base.domain.model.proxy.parser;

import lombok.extern.slf4j.Slf4j;
import org.apache.hc.client5.http.cookie.Cookie;
import org.apache.hc.core5.http.ClassicHttpResponse;
import org.apache.hc.core5.http.Header;
import org.apache.hc.core5.http.ParseException;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Component
public class CookieParser {
    public Cookie parseString(String value) {
        return null;
    }
    public List<Cookie> parseHttpResponse(ClassicHttpResponse response)
            throws IOException, ParseException{
        List<Cookie> cookies = new ArrayList<>();
        Header[] setCookieHeaders = response.getHeaders("Set-Cookie");
        return cookies;
    }
}
