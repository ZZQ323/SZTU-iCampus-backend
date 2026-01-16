package cn.edu.sztui.base.application.dto.command;

import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import lombok.Data;

@Data
public class LoginRequestCommand {
    private String wxCode;
    private String userId;
    private String password;
    private String smsCode;
    private LoginType loginType;
}
