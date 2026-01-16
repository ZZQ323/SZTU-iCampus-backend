package cn.edu.sztui.base.domain.model;

public interface SchoolAPIs {
    final String gatewayStartURL ="https://home.sztu.edu.cn/bmportal";
    final String gatewayEndURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/authcenter/ActionAuthChain?entityId=webvpn";

    final String smsURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/sendSMSCheckCode.do";
    final String loginURL ="https://auth-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/idp/authcenter/ActionAuthChain";
    final String logoutURL ="https://home-sztu-edu-cn-s.webvpn.sztu.edu.cn:8118/bmportal/logout.portal";
}
