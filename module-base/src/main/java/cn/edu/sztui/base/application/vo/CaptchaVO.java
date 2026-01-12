package cn.edu.sztui.base.application.vo;

import lombok.Data;
import org.apache.hc.client5.http.cookie.Cookie;
import java.util.List;

@Data
public class CaptchaVO {
    List<Cookie> cookies;
    String captchaBase64;
}
