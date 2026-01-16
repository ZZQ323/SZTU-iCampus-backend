package cn.edu.sztui.base.application.vo;

import com.microsoft.playwright.options.Cookie;
import lombok.Data;

import java.util.List;

/**
 * FIXME 仅测试！
 */
@Data
public class LoginResultsVo {
    List<Cookie> cookies;
}
