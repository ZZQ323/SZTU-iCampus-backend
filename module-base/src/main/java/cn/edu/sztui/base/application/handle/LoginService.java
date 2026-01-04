package cn.edu.sztui.base.application.handle;

import cn.edu.sztui.base.application.vo.LoginResultsVo;


public interface LoginService {
    final String loginURL ="https://home.sztu.edu.cn/bmportal";

    LoginResultsVo handleLoginByType();
}
