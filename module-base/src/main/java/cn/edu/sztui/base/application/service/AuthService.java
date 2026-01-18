package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.vo.LoginResultsVo;

import java.util.List;

public interface AuthService {

    boolean getSessionStatus();

    List<String> getPossibleUsrId();

    LoginResultsVo init();

    void getSms(String usrId);

    LoginResultsVo loginFrame(LoginRequestCommand cmd);

    LoginResultsVo logout(LoginRequestCommand cmd);
}
