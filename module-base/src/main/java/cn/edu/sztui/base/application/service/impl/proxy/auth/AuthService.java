package cn.edu.sztui.base.application.service.impl.proxy.auth;

import cn.edu.sztui.base.application.dto.command.ProxyLoginCommand;
import cn.edu.sztui.base.infrastructure.constants.LoginType;
import java.util.Map;

/**
 * 认证服务策略接口
 */
public interface AuthService {

    /**
     * 获取支持的登录类型
     */
    LoginType getSupportedType();

    /**
     * 构建登录表单数据
     */
    Map<String, String> buildFormData(ProxyLoginCommand command);
}
