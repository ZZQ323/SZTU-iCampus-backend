package cn.edu.sztui.base.application.dto.command;

import cn.edu.sztui.base.domain.model.logintype.LoginType;
import com.microsoft.playwright.options.Cookie;
import lombok.Data;

import java.util.List;

@Data
public class LoginRequestCommand {
    private String userId;
    private String code;
    List<Cookie> cookies;
    LoginType loginType;
}
