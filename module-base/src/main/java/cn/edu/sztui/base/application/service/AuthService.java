package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.vo.LoginBasicResultVO;
import cn.edu.sztui.base.application.vo.LoginResultsVo;

import java.util.List;

public interface AuthService {

    boolean getSessionStatus();

    List<String> getPossibleUsrId();

    LoginResultsVo init();

    LoginResultsVo getSms(String usrId);

    LoginBasicResultVO loginFrame(LoginRequestCommand cmd);

    LoginResultsVo logout(LoginRequestCommand cmd);
}
