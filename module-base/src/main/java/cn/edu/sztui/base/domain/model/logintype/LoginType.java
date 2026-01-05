package cn.edu.sztui.base.domain.model.logintype;

import lombok.Getter;

// 登录方式枚举（映射页面authMethodIDs的值和tabCon的ID）
public enum LoginType {
    // 用户名密码
    USERNAME_PASSWORD(1, "tab1Con", "j_username", "j_password","用户名密码"),
    // 证书认证（无输入框）
    CERT(2, "tab2Con", "", "","证书认证（无输入框）"),
    // 用户名+OTP
    OTP(3, "tab3Con", "fs31_username", "fs31_otpOrSms","用户名+OTP"),
    // 用户名+短信验证码
    SMS(4, "smsBtn1", "fs41_username", "sms1_otpOrSms","用户名+短信验证码"),
    // 用户名密码+证书
    USER_PWD_CERT(5, "tab5Con", "fs5_username", "fs5_password","用户名密码+证书"),
    // e账通二维码
    EPASS_QR(10, "tab10Con", "", "","e账通二维码"),
    // 钉钉
    DINGDING(11, "tab11Con", "", "","钉钉"),
    // 微信
    WECHAT(12, "tab12Con", "", "","微信"),
    // 静脉认证
    VEIN(13, "tab13Con", "userCode", "","静脉认证"),
    // 第三方APP二维码
    THIRD_APP(20, "tab20Con", "", "","第三方APP二维码");

    // getter方法
    @Getter
    private final int authId; // 对应页面authMethodIDs的值
    @Getter
    private final String tabConId; // 对应tabCon的ID
    @Getter
    private final String usernameInputId; // 用户名输入框ID
    @Getter
    private final String codeInputId; // 密码/验证码输入框ID
    @Getter
    private final String descriptionMsg;

    LoginType(int authId, String tabConId, String usernameInputId, String codeInputId, String descriptionInputId) {
        this.authId = authId;
        this.tabConId = tabConId;
        this.usernameInputId = usernameInputId;
        this.codeInputId = codeInputId;
        this.descriptionMsg = descriptionInputId;
    }

    // 根据authMethodIDs的值获取登录方式
    public static LoginType getByAuthId(int authId) {
        for (LoginType type : LoginType.values()) {
            if (type.authId == authId) {
                return type;
            }
        }
        return null;
    }

}

