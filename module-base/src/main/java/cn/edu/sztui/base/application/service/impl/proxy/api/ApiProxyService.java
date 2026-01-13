package cn.edu.sztui.base.application.service.impl.proxy.api;

import cn.edu.sztui.base.domain.model.proxy.SchoolHttpClient;
import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import jakarta.annotation.Resource;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

import java.io.IOException;

@Slf4j
@Component
@RequiredArgsConstructor
public class ApiProxyService {

    @Resource
    private final SchoolHttpClient httpClient;
    @Resource
    private final ProxySessionCacheUtil sessionCache;
    @Resource
    private ProxySessionCacheUtil proxySessionCacheUtil;

    public String proxyApi(String machineId, String userId, String apiUrl) {
        log.info("代理API, machineId: {}, userId: {}, url: {}", machineId, userId, apiUrl);

        if(proxySessionCacheUtil.hasUserSession(machineId, userId)){
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),"会话不存在", ResultCodeEnum.UNAUTHORIZED.getCode());
        }
        // proxySessionCacheUtil.restoreUserSessionCookies(machineId, userId);

        try {
            HttpResult result = httpClient.doGet(machineId, apiUrl);

            // Session 过期检查
            if (result.getFinalUrl() != null && result.getFinalUrl().contains("login")) {
                sessionCache.removeUserSession(machineId, userId);
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                        "会话已过期，请重新登录", ResultCodeEnum.UNAUTHORIZED.getCode());
            }

            // 更新 Cookie
            if (!CollectionUtils.isEmpty(result.getCookies())) {
                sessionCache.updateUserSessionCookies(machineId, userId, result.getCookies());
            }

            return result.getBody();

        } catch (BusinessException e) {
            throw e;
        } catch (IOException e) {
            log.error("代理API失败", e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "请求失败：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }

    public String proxyApi(String machineId, String apiUrl) {
        String userId = sessionCache.getActiveAccount(machineId);
        if (userId == null) {
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "未登录，请先登录", ResultCodeEnum.UNAUTHORIZED.getCode());
        }
        return proxyApi(machineId, userId, apiUrl);
    }
}
