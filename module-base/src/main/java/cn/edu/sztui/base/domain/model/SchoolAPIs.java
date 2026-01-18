package cn.edu.sztui.base.domain.model;

public interface SchoolAPIs {
    final String gatewayStartURL ="https://home.sztu.edu.cn/bmportal";
    final String gatewayFirstEndURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/authcenter/ActionAuthChain?entityId=webvpn";
    final String gatewaySecondEndURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/authcenter/ActionAuthChain?entityId=home";
    final String smsURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/sendSMSCheckCode.do";
    final String loginURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/authcenter/ActionAuthChain";
    final String A4tLoginFormActionURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/AuthnEngine?currentAuth=urn_oasis_names_tc_SAML_2.0_ac_classes_SMSUsernamePassword";
    final String spAuthChainCode ="3c21e7d55f6449df85e8cebc30518464";
    final String logoutURL ="https://home-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/bmportal/logout.portal";

    // academic administration system
    final String AASysGatewayURL ="https://jwxt-sztu-edu-cn.webvpn.sztu.edu.cn:8118/";
    final String AASysSwitchPort = "https://jwxt-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/jsxsd/framework/xsrkxz.htmlx";
    final String AcdemAdminSysURL = "https://jwxt-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/jsxsd/framework/xsMain.jsp";
    final String acdemAdminSysGatewayStartURL = "https://home-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/bmportal/index.portal";
    final String scheduleTableURL = "https://jwxt-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/jsxsd/xskb/xskb_list.do";
}
