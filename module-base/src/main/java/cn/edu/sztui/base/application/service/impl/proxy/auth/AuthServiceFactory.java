package cn.edu.sztui.base.application.service.impl.proxy.auth;

import cn.edu.sztui.base.infrastructure.constants.LoginType;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@RequiredArgsConstructor
public class AuthServiceFactory {

    private final List<AuthService> authServices;

    public AuthService getAuthService(LoginType loginType) {
        return authServices.stream()
                .filter(s -> s.getSupportedType() == loginType)
                .findFirst()
                .orElseThrow(() -> new BusinessException(
                        SysReturnCode.BASE_PROXY.getCode(),
                        "不支持的登录类型: " + loginType,
                        ResultCodeEnum.BAD_REQUEST.getCode()));
    }
}