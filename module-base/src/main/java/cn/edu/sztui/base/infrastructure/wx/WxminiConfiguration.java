package cn.edu.sztui.base.infrastructure.wx;

import cn.binarywang.wx.miniapp.api.WxMaService;
import cn.binarywang.wx.miniapp.api.impl.WxMaServiceImpl;
import cn.binarywang.wx.miniapp.config.WxMaConfig;
import cn.binarywang.wx.miniapp.config.impl.WxMaDefaultConfigImpl;
import lombok.Data;
import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

/**
 * @see https://gitee.com/binary/weixin-java-miniapp-demo/blob/master/src/main/java/com/github/binarywang/demo/wx/miniapp/config/WxMaConfiguration.java
 * @see https://gitee.com/binary/weixin-java-miniapp-demo/blob/master/src/main/java/com/github/binarywang/demo/wx/miniapp/config/WxMaProperties.java
 */

@Data
@Component
public class WxminiConfiguration{
    @Value("${wx.miniapp.configs.appid}")
    private String appid;
    @Value("${wx.miniapp.configs.secret}")
    private String secret;
    @Value("${wx.miniapp.configs.secret}")
    private String token;
    @Value("${wx.miniapp.configs.aesKey}")
    private String aesKey;
    @Value("${wx.miniapp.configs.rsaKey}")
    private String rsaKey;
    @Value("${wx.miniapp.configs.msgDataFormat}")
    private String msgDataFormat;

    @Getter
    private WxMaService wxService;


    // 手动配置 Bean 进行 WxMaService的注入
    @Bean
    public WxMaConfig wxMaConfig() {
        WxMaDefaultConfigImpl config = new WxMaDefaultConfigImpl();
        config.setAppid(appid);
        config.setSecret(secret);
        config.setToken(token);
        config.setAesKey(aesKey);
        config.setMsgDataFormat("JSON");
        return config;
    }

    @Bean
    public WxMaService wxMaService(WxMaConfig wxMaConfig) {
        WxMaService wxMaService = new WxMaServiceImpl();
        wxMaService.setWxMaConfig(wxMaConfig);
        return wxMaService;
    }
}
