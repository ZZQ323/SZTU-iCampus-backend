package cn.edu.sztui.base.application.vo;

import lombok.Data;
import org.apache.http.cookie.Cookie;

import java.util.List;

@Data
public class CaptchaVO {
    List<Cookie> cookies;
    String captchaBase64;
}
