package cn.edu.sztui.base.domain.model.proxy.parser;

import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class LoginResultParser {

    public boolean needsCaptcha(HttpResult result) {
        return false;
    }

    public boolean isLoginSuccess(HttpResult result) {
        return false;
    }

    public String extractErrorMessage(String body) {
        return "false";
    }
}
