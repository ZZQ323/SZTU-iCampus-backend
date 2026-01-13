package cn.edu.sztui.base.application.vo;

import lombok.Data;
import org.apache.http.cookie.Cookie;

import java.util.List;

@Data
public class LoginResultsVo {
    private String userId;
    private String passwd;
    List<Cookie> cookies;
    String htmlDoc;
}
