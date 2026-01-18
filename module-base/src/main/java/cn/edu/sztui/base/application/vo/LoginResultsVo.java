package cn.edu.sztui.base.application.vo;

import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import com.microsoft.playwright.options.Cookie;
import lombok.Data;

import java.util.List;


@Data
public class LoginResultsVo {
    // FIXME 仅测试返回！
    List<Cookie> cookies;
    String content;
    // 允许的登录方式
    List<LoginType> loginTypes;
}
