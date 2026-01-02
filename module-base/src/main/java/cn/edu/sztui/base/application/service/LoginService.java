package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.vo.LoginResultsVo;


public interface LoginService {
    LoginResultsVo loginWithPasswd(String username, String password);

//    LoginResultsVo loginWithVerifyCode(String username, String verficationCode);
}
