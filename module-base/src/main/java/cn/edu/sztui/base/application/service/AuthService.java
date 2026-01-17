package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.vo.LoginBasicResultVO;
import cn.edu.sztui.base.application.vo.LoginResultsVo;

public interface AuthService {

    boolean getSessionStatus(String tempCode);

    LoginResultsVo init(String tempCode);

    LoginResultsVo getSms(String tempCode, String usrId);

    LoginBasicResultVO loginFrame(LoginRequestCommand cmd);

    LoginResultsVo logout(LoginRequestCommand cmd);
}
