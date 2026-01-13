package cn.edu.sztui.base.application.service.impl.proxy.api;

import cn.edu.sztui.base.application.dto.command.ProxyLoginCommand;
import cn.edu.sztui.base.application.service.impl.proxy.auth.AuthService;
import cn.edu.sztui.base.application.service.impl.proxy.auth.AuthServiceFactory;
import cn.edu.sztui.base.application.vo.ProxyLoginResultVO;
import cn.edu.sztui.base.domain.model.proxy.SchoolHttpClient;
import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import cn.edu.sztui.base.domain.model.proxy.parser.LoginResultParser;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import jakarta.annotation.Resource;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.cookie.Cookie;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class LoginService {

    @Resource
    private final SchoolHttpClient httpClient;
    @Resource
    private final ProxySessionCacheUtil sessionCache;
    @Resource
    private final AuthServiceFactory authServiceFactory;
    @Resource
    private final ProxySessionCacheUtil proxySessionCacheUtil;

    @Resource
    private final LoginResultParser resultParser;

    @Value("${school.url.login}")
    private String loginUrl;

    public ProxyLoginResultVO login(ProxyLoginCommand command) {
        String machineId = command.getMachineId();
        String userId = command.getUserId();

        log.info("登录, machineId: {}, userId: {}, type: {}",
                machineId, userId, command.getLoginType());
        proxySessionCacheUtil.hasDeviceInitSession(machineId);
        // proxySessionCacheUtil.restoreDeviceInitCookies(machineId);
        try {
            AuthService authService = authServiceFactory.getAuthService(command.getLoginType());
            Map<String, String> formData = authService.buildFormData(command);
            HttpResult result = httpClient.doPostWithManualRedirect(
                    machineId, loginUrl + "?sf_request_type=ajax", 15,formData);
            // 检查是否需要图形验证码
            if (resultParser.needsCaptcha(result)) {
                return ProxyLoginResultVO.builder()
                        .success(false)
                        .isNeedCaptcha(true)
                        .message("需要图形验证码")
                        .build();
            }
            if (resultParser.isLoginSuccess(result)) {
                List<Cookie> loginCookies = httpClient.getUserCookies(machineId);
                sessionCache.createUserSession(machineId, userId, loginCookies);
                log.info("登录成功, machineId: {}, userId: {}", machineId, userId);
                return ProxyLoginResultVO.builder()
                        .success(true)
                        .machineId(machineId)
                        .userId(userId)
                        .message("登录成功")
                        .build();
            } else {
                String errorMsg = resultParser.extractErrorMessage(result.getBody());
                log.warn("登录失败: {}", errorMsg);

                return ProxyLoginResultVO.builder()
                        .success(false)
                        .message(errorMsg)
                        .build();
            }

        } catch (Exception e) {
            log.error("登录请求失败", e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "登录请求失败：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }
}