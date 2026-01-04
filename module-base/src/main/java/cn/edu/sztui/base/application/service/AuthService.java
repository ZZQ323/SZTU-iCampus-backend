package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.LoginType;


public interface AuthService {

    LoginType loginCheck();

    LoginResultsVo loginFrame(LoginRequestCommand cmd);

    LoginResultsVo getSms(String id);

//    LoginResultsVo loginWithVerifyCode(String username, String verficationCode);
}
