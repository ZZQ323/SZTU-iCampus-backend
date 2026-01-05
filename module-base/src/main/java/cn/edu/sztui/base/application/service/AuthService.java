package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;


public interface AuthService {

    LoginType loginCheck();

    LoginResultsVo loginFrame(LoginRequestCommand cmd);

    LoginResultsVo getSms(String id);

    String logout();

//    LoginResultsVo loginWithVerifyCode(String username, String verficationCode);
}
