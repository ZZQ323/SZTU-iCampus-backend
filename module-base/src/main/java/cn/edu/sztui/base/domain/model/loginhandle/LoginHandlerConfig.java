package cn.edu.sztui.base.domain.model.loginhandle;

import cn.edu.sztui.base.domain.model.loginhandle.impl.*;
import jakarta.annotation.Resource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

@Configuration
public class LoginHandlerConfig {

    // 注入所有LoginHandle实现类（确保这些类已被Spring管理，比如加了@Component）
    @Resource
    private UsernamePasswordImpl usernamePasswordImpl;
    @Resource
    private CertificateImpl certificateImpl;
    @Resource
    private UsernameOtpImpl usernameOtpImpl;
    @Resource
    private UsernameSmsImpl usernameSmsImpl;
    @Resource
    private QrCodeImpl qrCodeImpl;
    @Resource
    private SsoImpl ssoImpl;
    @Resource
    private BiometricImpl biometricImpl;

    /**
     * 初始化 LoginType -> LoginHandle 的映射关系
     * 使用HashMap（支持后续扩展），并包装为不可变Map防止篡改
     */
    @Bean
    public Map<LoginType, LoginHandle> loginHandlers() {
        Map<LoginType, LoginHandle> map = new HashMap<>();
        // 逐个映射，此时所有impl都已被Spring注入，非null
        map.put(LoginType.USERNAME_PASSWORD, usernamePasswordImpl);
        map.put(LoginType.USER_PWD_CERT, certificateImpl);
        map.put(LoginType.OTP, usernameOtpImpl);
        map.put(LoginType.SMS, usernameSmsImpl);
        map.put(LoginType.EPASS_QR, qrCodeImpl);
        map.put(LoginType.WECHAT, qrCodeImpl);
        map.put(LoginType.THIRD_APP, qrCodeImpl);
        map.put(LoginType.DINGDING, ssoImpl);
        map.put(LoginType.CERT, certificateImpl);
        map.put(LoginType.VEIN, biometricImpl);
        // 包装为不可变Map，保证线程安全
        return Collections.unmodifiableMap(map);
    }
}
