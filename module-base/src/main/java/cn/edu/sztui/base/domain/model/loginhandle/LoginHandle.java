package cn.edu.sztui.base.domain.model.loginhandle;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.domain.model.loginhandle.impl.UsernamePasswordImpl;
import cn.edu.sztui.base.domain.model.loginhandle.impl.UsernameSmsImpl;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.BrowserContext;

public interface LoginHandle {
    /**
     * 静态工厂方法 - 创建新的实例（不依赖Spring）
     */
    static LoginHandle createLoginHandle(LoginType type) {
        return switch (type) {
            case SMS -> new UsernameSmsImpl();
            case PASSWORD -> new UsernamePasswordImpl();
//            case OTP -> new UsernameOtpImpl();
            default -> throw new IllegalArgumentException("不支持的登录类型: " + type);
        };
    }
    /**
     * 获取登录类型
     */
    default LoginType getLoginType(){
        return null;
    }


    default  APIResponse loginVerification(BrowserContext context, LoginRequestCommand cmd){
        return null;
    }

    default  APIResponse loginRedirect(BrowserContext context, LoginRequestCommand cmd){
        return null;
    }
}