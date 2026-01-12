package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.dto.command.ProxyLoginCommand;
import cn.edu.sztui.base.application.vo.ProxyInitVO;
import cn.edu.sztui.base.application.vo.ProxyLoginResultVO;

public interface ProxyService {

    ProxyInitVO initSession(String code,String deviceToken);

    boolean sendSms(String machineId, String userId);

    ProxyLoginResultVO login(ProxyLoginCommand command);

    String proxyApi(String machineId, String apiUrl);

    boolean checkSession(String machineId);

    void logout(String machineId);
}
