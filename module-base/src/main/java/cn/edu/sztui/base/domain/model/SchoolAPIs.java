package cn.edu.sztui.base.domain.model;

public interface SchoolAPIs {
    final String gatewayStartURL ="https://home.sztu.edu.cn/bmportal";
    final String gatewayEndURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/authcenter/ActionAuthChain?entityId=webvpn";

    final String smsURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/sendSMSCheckCode.do";
    final String loginURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/authcenter/ActionAuthChain";
    final String A4tLoginFormActionURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/AuthnEngine?currentAuth=urn_oasis_names_tc_SAML_2.0_ac_classes_SMSUsernamePassword";
    final String spAuthChainCode ="3c21e7d55f6449df85e8cebc30518464";
    final String logoutURL ="https://home-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/bmportal/logout.portal";
    final String logoutEndURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/authcenter/ActionAuthChain?entityId=home";
}
