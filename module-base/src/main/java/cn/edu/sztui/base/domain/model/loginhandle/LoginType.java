package cn.edu.sztui.base.domain.model.loginhandle;

import cn.edu.sztui.base.domain.model.loginhandle.impl.*;
import jakarta.annotation.Resource;
import lombok.Getter;
import java.util.Map;

/**
 * 登录方式枚举 - 重构版
 * 按照交互模式分类，提供完整的元素定位信息
 */
public enum LoginType {

    // ========== 用户名密码类 ==========
    USERNAME_PASSWORD(
            1, "tab1Con", "用户名密码",
            InteractionMode.USERNAME_PASSWORD,
            new LoginConfig()
                    .setUsernameInputId("j_username")
                    .setPasswordInputId("j_password")
                    .setLoginButtonId("loginButton")
    ),
    //
    USER_PWD_CERT(
            5, "tab5Con", "用户名密码+证书",
            InteractionMode.USERNAME_PASSWORD,
            new LoginConfig()
                    .setUsernameInputId("fs5_username")
                    .setPasswordInputId("fs5_password")
                    .setLoginButtonSelector("#tab5Con button.loginBt")
    ),

    // ========== 用户名+动态验证码类 ==========
    OTP(
            3, "tab3Con", "用户名+OTP",
            InteractionMode.USERNAME_OTP,
            new LoginConfig()
                    .setUsernameInputId("fs31_username")
                    .setOtpInputId("fs31_otpOrSms")
                    .setLoginButtonSelector("#tab3Con button.loginBt")
    ),
    //
    SMS(
            4, "tab4Con", "用户名+短信验证码",
            InteractionMode.USERNAME_SMS,
            new LoginConfig()
                    .setUsernameInputId("fs41_username")
                    .setSmsInputId("sms1_otpOrSms")
                    .setSendSmsButtonId("smsBtn1")
                    .setLoginButtonId("smsLoginBtn")
    ),

    // ========== 二维码类 ==========
    EPASS_QR(
            10, "tab10Con", "e账通二维码",
            InteractionMode.QR_CODE,
            new LoginConfig()
                    .setQrImageId("QRImage")
                    .setSessionIdInputId("epsessionId_1_10")
    ),
    //
    WECHAT(
            12, "tab12Con", "微信",
            InteractionMode.QR_CODE,
            new LoginConfig()
                    .setQrImageId("wx_QRImage")
                    .setQrTokenInputId("qrCodeToken")
                    .setRefreshButtonId("refreashWechatQrCodeBtn")
    ),
    //
    THIRD_APP(
            20, "tab20Con", "第三方APP二维码",
            InteractionMode.QR_CODE,
            new LoginConfig()
                    .setQrImageId("thirdappQRImage")
                    .setQrTokenInputId("thirdappqrCodeToken")
                    .setRefreshButtonId("refreashThirdAppQrCodeBtn")
    ),

    // ========== 单点登录类 ==========
    DINGDING(
            11, "tab11Con", "钉钉",
            InteractionMode.SSO,
            new LoginConfig()
                    .setSsoContainerId("login_container_temp")
    ),

    // ========== 证书类 ==========
    CERT(
            2, "tab2Con", "证书认证",
            InteractionMode.CERTIFICATE,
            new LoginConfig()
                    .setLoginButtonSelector("#tab2Con button.loginBt")
    ),

    // ========== 生物识别类 ==========
    VEIN(
            13, "tab13Con", "静脉认证",
            InteractionMode.BIOMETRIC,
            new LoginConfig()
                    .setUsernameInputId("userCode")
                    .setCaptureButtonId("captureBtn")
                    .setSubmitButtonId("verifyBtn")
    );

    @Getter private final int authId;
    @Getter private final String tabConId;
    @Getter private final String description;
    @Getter private final InteractionMode mode;
    @Getter private final LoginConfig config;

    LoginType(int authId, String tabConId, String description,
              InteractionMode mode, LoginConfig config) {
        this.authId = authId;
        this.tabConId = tabConId;
        this.description = description;
        this.mode = mode;
        this.config = config;
    }

    public static LoginType getByAuthId(int authId) {
        for (LoginType type : LoginType.values()) {
            if (type.authId == authId) {
                return type;
            }
        }
        return null;
    }

    /**
     * 交互模式枚举
     */
    public enum InteractionMode {
        /** 用户名+密码 直接登录 */
        USERNAME_PASSWORD,

        /** 用户名+OTP 直接登录 */
        USERNAME_OTP,

        /** 用户名+短信验证码（需要先发送验证码） */
        USERNAME_SMS,

        /** 二维码扫描登录 */
        QR_CODE,

        /** 单点登录（第三方） */
        SSO,

        /** 证书认证 */
        CERTIFICATE,

        /** 生物识别 */
        BIOMETRIC
    }

    /**
     * 登录配置类 - 使用建造者模式
     */
    @Getter
    public static class LoginConfig {
        // 输入框ID
        private String usernameInputId;
        private String passwordInputId;
        private String otpInputId;
        private String smsInputId;

        // 按钮ID或选择器
        private String loginButtonId;
        private String loginButtonSelector;
        private String sendSmsButtonId;
        private String captureButtonId;
        private String submitButtonId;
        private String refreshButtonId;

        // 二维码相关
        private String qrImageId;
        private String qrTokenInputId;
        private String sessionIdInputId;

        // SSO相关
        private String ssoContainerId;

        // 建造者方法
        public LoginConfig setUsernameInputId(String id) {
            this.usernameInputId = id;
            return this;
        }

        public LoginConfig setPasswordInputId(String id) {
            this.passwordInputId = id;
            return this;
        }

        public LoginConfig setOtpInputId(String id) {
            this.otpInputId = id;
            return this;
        }

        public LoginConfig setSmsInputId(String id) {
            this.smsInputId = id;
            return this;
        }

        public LoginConfig setLoginButtonId(String id) {
            this.loginButtonId = id;
            return this;
        }

        public LoginConfig setLoginButtonSelector(String selector) {
            this.loginButtonSelector = selector;
            return this;
        }

        public LoginConfig setSendSmsButtonId(String id) {
            this.sendSmsButtonId = id;
            return this;
        }

        public LoginConfig setCaptureButtonId(String id) {
            this.captureButtonId = id;
            return this;
        }

        public LoginConfig setSubmitButtonId(String id) {
            this.submitButtonId = id;
            return this;
        }

        public LoginConfig setRefreshButtonId(String id) {
            this.refreshButtonId = id;
            return this;
        }

        public LoginConfig setQrImageId(String id) {
            this.qrImageId = id;
            return this;
        }

        public LoginConfig setQrTokenInputId(String id) {
            this.qrTokenInputId = id;
            return this;
        }

        public LoginConfig setSessionIdInputId(String id) {
            this.sessionIdInputId = id;
            return this;
        }

        public LoginConfig setSsoContainerId(String id) {
            this.ssoContainerId = id;
            return this;
        }

        /**
         * 获取登录按钮的定位符（优先使用selector，其次使用id）
         */
        public String getLoginButtonLocator() {
            if (loginButtonSelector != null) {
                return loginButtonSelector;
            }
            if (loginButtonId != null) {
                return "#" + loginButtonId;
            }
            return null;
        }
    }
}