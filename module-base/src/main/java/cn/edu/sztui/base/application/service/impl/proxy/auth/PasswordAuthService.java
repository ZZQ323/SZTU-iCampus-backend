package cn.edu.sztui.base.application.service.impl.proxy.auth;

import cn.edu.sztui.base.application.dto.command.ProxyLoginCommand;
import cn.edu.sztui.base.infrastructure.constants.LoginType;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

@Component
public class PasswordAuthService implements AuthService {

    @Override
    public LoginType getSupportedType() {
        return LoginType.PASSWORD;
    }

    @Override
    public Map<String, String> buildFormData(ProxyLoginCommand command) {
        Map<String, String> formData = new HashMap<>();
        formData.put("j_username", command.getUserId());
        formData.put("j_password", command.getCode());
        formData.put("authMethodIDs", "2");
        formData.put("tabFromId", "tabFrom2");
        return formData;
    }
}
