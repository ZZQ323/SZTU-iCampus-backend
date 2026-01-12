package cn.edu.sztui.base.application.dto.command;

import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import lombok.Data;
import org.apache.hc.client5.http.cookie.Cookie;

import java.util.List;

@Data
public class LoginRequestCommand {
    private String userId;
    private String code;
    List<Cookie> cookies;
    LoginType loginType;
}
