package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.vo.LoginResultsVo;


public interface AuthServiceV1 {

    LoginResultsVo getSms(String id);

    LoginResultsVo loginFrame(LoginRequestCommand cmd);

    LoginResultsVo loginByCookie(LoginRequestCommand cmd);

    String logout();

//    LoginResultsVo loginWithVerifyCode(String username, String verficationCode);
}
