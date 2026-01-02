package cn.edu.sztui.base.application.vo;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.Cookie;
import lombok.Data;

import java.util.List;

@Data
public class LoginResultsVo {
    private int statusCode;
    private String message;
    
    private String userId;
    private String passwd;
    List<Cookie> cookies;
    Page page;
}
