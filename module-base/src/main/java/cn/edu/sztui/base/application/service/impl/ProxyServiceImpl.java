package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.ProxyLoginCommand;
import cn.edu.sztui.base.application.service.ProxyService;
import cn.edu.sztui.base.application.service.impl.proxy.api.ApiProxyService;
import cn.edu.sztui.base.application.service.impl.proxy.api.LoginService;
import cn.edu.sztui.base.application.service.impl.proxy.auth.SmsAuthService;
import cn.edu.sztui.base.application.service.impl.proxy.lifespan.AccountManager;
import cn.edu.sztui.base.application.service.impl.proxy.lifespan.SessionInitializer;
import cn.edu.sztui.base.application.service.impl.proxy.lifespan.SessionValidator;
import cn.edu.sztui.base.application.vo.ProxyInitVO;
import cn.edu.sztui.base.application.vo.ProxyLoginResultVO;
import cn.edu.sztui.base.domain.model.wxmini.WechatDeviceServiceImpl;
import jakarta.annotation.Resource;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Set;

/**
 * 代理服务实现 - 重构后的门面类
 * 职责：协调各专门化组件完成业务流程
 *
 * <h2>登录流程</h2>
 * <pre>
 * 1. initSession(machineId)
 *    └─ 访问网关 → 获取初始 Cookie → 存入 device:init:{machineId}
 *
 * 2. sendSms(machineId, userId)
 *    └─ 使用 device:init Cookie → 请求短信 → 更新 device:init Cookie
 *
 * 3. login(machineId, userId, code)
 *    └─ 使用 device:init Cookie → 登录验证 → 成功后:
 *       - 删除 device:init
 *       - 创建 session:{machineId}:{userId}
 *       - 更新 device:accounts 和 device:active
 *
 * 4. proxyApi(machineId, userId, url)
 *    └─ 使用 session:{machineId}:{userId} Cookie → 访问 API
 * </pre>
 *
 * <h2>账号切换</h2>
 * <pre>
 * - switchAccount(machineId, userId): 切换到另一个已登录账号
 * - getAccounts(machineId): 获取设备上所有已登录账号
 * </pre>
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ProxyServiceImpl implements ProxyService {

    @Resource
    private final SessionInitializer sessionInitializer;
    @Resource
    private final SessionValidator sessionValidator;
    @Resource
    private final SmsAuthService smsAuthService;
    @Resource
    private final LoginService loginService;
    @Resource
    private final ApiProxyService apiProxyService;
    @Resource
    private final AccountManager accountManager;

    @Resource
    private WechatDeviceServiceImpl wechatDeviceServiceImpl;

    // ==================== 1. 初始化会话 ====================

    @Override
    public ProxyInitVO initSession(String code, String deviceToken) {
        // String machineId = wechatDeviceServiceImpl.getWechatDeviceId(code, deviceToken);
        String machineId = "testing"; // TODO: 上线前替换
        return sessionInitializer.initSession(machineId);
    }

    // ==================== 2. 发送短信 ====================

    @Override
    public boolean sendSms(String machineId, String userId) {
        return smsAuthService.sendSms(machineId, userId);
    }

    // ==================== 3. 登录 ====================

    @Override
    public ProxyLoginResultVO login(ProxyLoginCommand command) {
        return loginService.login(command);
    }

    // ==================== 4. 代理访问 API ====================

    @Override
    public String proxyApi(String machineId, String apiUrl) {
        return apiProxyService.proxyApi(machineId, apiUrl);
    }

    public String proxyApi(String machineId, String userId, String apiUrl) {
        return apiProxyService.proxyApi(machineId, userId, apiUrl);
    }

    // ==================== 5. 检查会话 ====================

    @Override
    public boolean checkSession(String machineId) {
        return sessionValidator.checkSession(machineId);
    }

    public boolean checkSession(String machineId, String userId) {
        return sessionValidator.checkSession(machineId, userId);
    }

    // ==================== 6. 登出 ====================

    @Override
    public void logout(String machineId) {
        accountManager.logout(machineId);
    }

    public void logout(String machineId, String userId) {
        accountManager.logout(machineId, userId);
    }

    // ==================== 7. 账号管理 ====================

    public Set<String> getDeviceAccounts(String machineId) {
        return accountManager.getDeviceAccounts(machineId);
    }

    public String getActiveAccount(String machineId) {
        return accountManager.getActiveAccount(machineId);
    }

    public boolean switchAccount(String machineId, String userId) {
        return accountManager.switchAccount(machineId, userId);
    }
}