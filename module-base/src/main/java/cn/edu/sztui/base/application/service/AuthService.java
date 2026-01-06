package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;


public interface AuthService {

    LoginType loginCheck();

    LoginResultsVo getSms(String id);

    LoginResultsVo loginFrame(LoginRequestCommand cmd);

    LoginResultsVo loginByCookie(LoginRequestCommand cmd);

    String logout();

//    LoginResultsVo loginWithVerifyCode(String username, String verficationCode);
}
