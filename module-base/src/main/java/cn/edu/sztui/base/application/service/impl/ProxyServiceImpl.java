package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.ProxyLoginCommand;
import cn.edu.sztui.base.application.service.ProxyService;
import cn.edu.sztui.base.application.vo.ProxyInitVO;
import cn.edu.sztui.base.application.vo.ProxyLoginResultVO;
import cn.edu.sztui.base.domain.model.Proxy.SchoolHttpClient;
import cn.edu.sztui.base.domain.model.Proxy.SchoolHttpClient.HttpResult;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil.ProxySession;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.hc.client5.http.cookie.Cookie;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 代理服务实现
 */
@Slf4j
@Service
public class ProxyServiceImpl  implements ProxyService {

    @Resource
    private SchoolHttpClient httpClient;

    @Resource
    private ProxySessionCacheUtil sessionCache;

    @Value("${school.url.gateway")
    private String gatewayUrl;
    @Value("${school.url.login")
    private String loginUrl;
    @Value("${school.url.sms-send")
    private String smsSendUrl;

    // ==================== 1. 初始化会话 ====================

    @Override
    public ProxyInitVO initSession() {
        String machineId = sessionCache.generateMachineId();
        log.info("初始化会话, machineId: {}", machineId);
        try {
            // 访问网关，触发OAuth重定向，获取初始Cookie
            HttpResult result = httpClient.doGetWithManualRedirect(machineId, gatewayUrl, 10);
            if (CollectionUtils.isEmpty(result.getCookies()))
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),"初始化失败：未获取到Cookie", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());

            // 保存机器会话
            sessionCache.saveMachineSession(machineId, result.getCookies());

            // 解析页面，提取表单token
            Document doc = Jsoup.parse(result.getBody());

            ProxyInitVO vo = new ProxyInitVO();
            vo.setMachineId(machineId);
            vo.setFinalUrl(result.getFinalUrl());
            vo.setLt(extractInputValue(doc, "lt"));
            vo.setExecution(extractInputValue(doc, "execution"));
            vo.setAuthMethodIDs(extractInputValue(doc, "authMethodIDs"));

            log.info("会话初始化成功, machineId: {}, cookies: {}", machineId, result.getCookies().size());
            return vo;

        } catch (IOException e) {
            log.error("初始化会话失败", e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "初始化失败：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }

    // ==================== 2. 发送短信 ====================

    @Override
    public boolean sendSms(String machineId, String phone) {
        log.info("发送短信, machineId: {}, phone: {}", machineId, phone);

        validateMachineSession(machineId);
        restoreCookiesToClient(machineId);

        try {
            // 模拟人类行为延迟
            randomDelay();

            Map<String, String> formData = new HashMap<>();
            formData.put("j_username1", phone);
            formData.put("authtype", "1");

            HttpResult result = httpClient.doPost(machineId, smsSendUrl, formData);

            // 更新Cookie
            if (!CollectionUtils.isEmpty(result.getCookies())) {
                sessionCache.updateSessionCookies(machineId, result.getCookies());
            }

            // 判断发送结果
            boolean success = result.isSuccess() &&
                    (result.getBody().contains("发送成功") ||
                            result.getBody().contains("success") ||
                            result.getBody().contains("\"code\":0"));

            log.info("短信发送{}, machineId: {}", success ? "成功" : "失败", machineId);
            return success;

        } catch (IOException e) {
            log.error("发送短信失败", e);
            return false;
        }
    }

    // ==================== 3. 登录 ====================

    @Override
    public ProxyLoginResultVO login(ProxyLoginCommand command) {
        String machineId = command.getMachineId();
        log.info("登录, machineId: {}, userId: {}, type: {}",
                machineId, command.getUserId(), command.getLoginType());

        validateMachineSession(machineId);
        restoreCookiesToClient(machineId);

        try {
            randomDelay();

            Map<String, String> formData = buildLoginFormData(command);
            HttpResult result = httpClient.doPost(machineId, loginUrl, formData);

            // 检查是否需要图形验证码
            if (result.getBody().contains("j_checkcodeImgCode") ||
                    result.getBody().contains("验证码")) {
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                        "需要图形验证码", ResultCodeEnum.BAD_REQUEST.getCode());
            }

            // 检查登录错误
            if (result.getBody().contains("错误") || result.getBody().contains("失败")) {
                String errorMsg = extractErrorMessage(result.getBody());
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                        "登录失败：" + errorMsg, ResultCodeEnum.BAD_REQUEST.getCode());
            }

            // 登录成功，可能需要跟随重定向到最终页面
            if (result.isSuccess() || result.isRedirect()) {
                HttpResult finalResult = httpClient.doGetWithManualRedirect(
                        machineId,
                        result.getFinalUrl() != null ? result.getFinalUrl() : gatewayUrl,
                        10
                );

                // 检查是否真的登录成功（没有被重定向回登录页）
                if (finalResult.getFinalUrl() != null &&
                        finalResult.getFinalUrl().contains("login")) {
                    throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                            "登录失败：被重定向回登录页", ResultCodeEnum.BAD_REQUEST.getCode());
                }

                // 绑定用户到机器会话
                sessionCache.bindUserToMachine(machineId, command.getUserId(), finalResult.getCookies());

                ProxyLoginResultVO vo = new ProxyLoginResultVO();
                vo.setMachineId(machineId);
                vo.setUserId(command.getUserId());
                vo.setSuccess(true);
                vo.setMessage("登录成功");

                log.info("登录成功, machineId: {}, userId: {}", machineId, command.getUserId());
                return vo;
            }

            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "登录失败：未知错误", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());

        } catch (BusinessException e) {
            throw e;
        } catch (IOException e) {
            log.error("登录失败", e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "登录失败：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }

    // ==================== 4. 代理访问API ====================

    @Override
    public String proxyApi(String machineId, String apiUrl) {
        log.debug("代理API, machineId: {}, url: {}", machineId, apiUrl);

        validateLoggedInSession(machineId);
        restoreCookiesToClient(machineId);

        try {
            HttpResult result = httpClient.doGet(machineId, apiUrl);

            // 检查是否被重定向到登录页（Session过期）
            if (result.getFinalUrl() != null && result.getFinalUrl().contains("login")) {
                sessionCache.removeSession(machineId);
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                        "会话已过期，请重新登录", ResultCodeEnum.UNAUTHORIZED.getCode());
            }

            // 更新Cookie
            if (!CollectionUtils.isEmpty(result.getCookies())) {
                sessionCache.updateSessionCookies(machineId, result.getCookies());
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

    // ==================== 5. 检查会话 ====================

    @Override
    public boolean checkSession(String machineId) {
        ProxySession session = sessionCache.getMachineSession(machineId);
        if (session == null) {
            return false;
        }

        // 如果已登录，尝试访问网关验证
        if (session.isLoggedIn()) {
            try {
                restoreCookiesToClient(machineId);
                HttpResult result = httpClient.doGet(machineId, gatewayUrl);
                boolean valid = result.getFinalUrl() == null ||
                        !result.getFinalUrl().contains("login");
                if (!valid) {
                    sessionCache.removeSession(machineId);
                }
                return valid;
            } catch (IOException e) {
                return false;
            }
        }

        return true;
    }

    // ==================== 6. 登出 ====================

    @Override
    public void logout(String machineId) {
        log.info("登出, machineId: {}", machineId);
        httpClient.clearUserCookies(machineId);
        sessionCache.removeSession(machineId);
    }

    // ==================== 辅助方法 ====================

    /**
     * 验证机器会话存在
     */
    private void validateMachineSession(String machineId) {
        if (!sessionCache.hasMachineSession(machineId)) {
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "会话不存在或已过期，请重新初始化", ResultCodeEnum.UNAUTHORIZED.getCode());
        }
    }

    /**
     * 验证已登录会话
     */
    private void validateLoggedInSession(String machineId) {
        validateMachineSession(machineId);
        if (!sessionCache.isLoggedIn(machineId)) {
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "未登录，请先登录", ResultCodeEnum.UNAUTHORIZED.getCode());
        }
    }

    /**
     * 从缓存恢复Cookie到HttpClient
     */
    private void restoreCookiesToClient(String machineId) {
        List<Cookie> cookies = sessionCache.getSessionCookies(machineId);
        if (!CollectionUtils.isEmpty(cookies)) {
            httpClient.clearUserCookies(machineId);
            httpClient.addCookies(machineId, cookies);
        }
    }

    /**
     * 构建登录表单数据
     */
    private Map<String, String> buildLoginFormData(ProxyLoginCommand command) {
        Map<String, String> formData = new HashMap<>();

        switch (command.getLoginType()) {
            case SMS -> {
                formData.put("j_username1", command.getUserId());
                formData.put("j_checkcode1", command.getCode());
                formData.put("authMethodIDs", "1");
                formData.put("tabFromId", "tabFrom1");
            }
            case PASSWORD -> {
                formData.put("j_username", command.getUserId());
                formData.put("j_password", command.getCode());
                formData.put("authMethodIDs", "2");
                formData.put("tabFromId", "tabFrom2");
            }
            case OTP -> {
                formData.put("j_username3", command.getUserId());
                formData.put("j_otp3", command.getCode());
                formData.put("authMethodIDs", "3");
                formData.put("tabFromId", "tabFrom3");
            }
            default -> throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "不支持的登录类型", ResultCodeEnum.BAD_REQUEST.getCode());
        }

        // 添加通用字段
        if (command.getLt() != null) {
            formData.put("lt", command.getLt());
        }
        if (command.getExecution() != null) {
            formData.put("execution", command.getExecution());
        }
        formData.put("_eventId", "submit");

        return formData;
    }

    /**
     * 提取表单隐藏字段值
     */
    private String extractInputValue(Document doc, String inputName) {
        var element = doc.selectFirst("input[name=" + inputName + "]");
        return element != null ? element.val() : null;
    }

    /**
     * 提取错误信息
     */
    private String extractErrorMessage(String html) {
        Document doc = Jsoup.parse(html);
        var errorElement = doc.selectFirst(".error-msg, .alert-danger, #errorMsg, .login-error");
        if (errorElement != null) {
            return errorElement.text();
        }
        return "未知错误";
    }

    /**
     * 随机延迟，模拟人类行为
     */
    private void randomDelay() {
        try {
            long delay = ThreadLocalRandom.current().nextLong(300, 1000);
            Thread.sleep(delay);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
