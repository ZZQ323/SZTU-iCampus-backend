package cn.edu.sztui.base.application.vo;

import cn.edu.sztui.common.util.enums.SysChannelEnum;
import com.microsoft.playwright.options.Cookie;
import lombok.Data;

import java.util.List;

@Data
public class LoginBasicResultVO {
    private Integer userId;
    private String unionId;
    private String phone;
    private String school;
    private String avatar;
    private SysChannelEnum sysChannel;
    // FIXME 仅测试返回！
    List<Cookie> cookies;
}
