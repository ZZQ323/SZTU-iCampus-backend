package cn.edu.sztui.base.domain.model.proxy.parser;

import lombok.extern.slf4j.Slf4j;
import org.apache.http.Header;
import org.apache.http.ParseException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.cookie.Cookie;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Component
public class CookieParser {



    public List<Cookie> parseHttpResponse(CloseableHttpResponse response)
            throws IOException, ParseException {
        List<Cookie> cookies = new ArrayList<>();
        Header[] setCookieHeaders = response.getHeaders("Set-Cookie");
        return cookies;
    }
}
