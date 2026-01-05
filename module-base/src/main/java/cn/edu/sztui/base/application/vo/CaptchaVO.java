package cn.edu.sztui.base.application.vo;

import com.microsoft.playwright.options.Cookie;
import lombok.Data;
import java.util.List;

@Data
public class CaptchaVO {
    List<Cookie> cookies;
    String captchaBase64;
}
