package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.ProxyLoginCommand;
import cn.edu.sztui.base.application.service.ProxyService;
import cn.edu.sztui.base.application.vo.ProxyInitVO;
import cn.edu.sztui.base.application.vo.ProxyLoginResultVO;
import cn.edu.sztui.base.domain.model.Proxy.SchoolHttpClient;
import cn.edu.sztui.base.domain.model.Proxy.SchoolHttpClient.HttpResult;
import cn.edu.sztui.base.domain.model.wxmini.WechatDeviceServiceImpl;
import cn.edu.sztui.base.infrastructure.persistence.CharacterConverter;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.hc.client5.http.cookie.Cookie;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 代理服务实现 - 重新设计版本
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
public class ProxyServiceImpl implements ProxyService {

    @Resource
    private SchoolHttpClient httpClient;

    @Resource
    private ProxySessionCacheUtil sessionCache;

    @Resource
    private WechatDeviceServiceImpl wechatDeviceServiceImpl;

    @Value("${school.url.gateway}")
    private String gatewayUrl;
    @Value("${school.url.login}")
    private String loginUrl;
    @Value("${school.url.sms-send}")
    private String smsSendUrl;

    // ==================== 1. 初始化会话 ====================

    /**
     * 初始化设备会话
     * <p>
     * 访问学校网关，触发 OAuth 重定向，获取初始 Cookie。
     * 这是登录流程的第一步，为后续的短信发送和登录做准备。
     * </p>
     *
     * @param code        微信授权码
     * @param deviceToken 设备令牌
     * @return 初始化结果，包含 machineId 和表单 token
     */
    @Override
    public ProxyInitVO initSession(String code, String deviceToken) {
        // 获取设备唯一标识
        // String machineId = wechatDeviceServiceImpl.getWechatDeviceId(code, deviceToken);
        String machineId = "testing"; // TODO: 上线前替换
        log.info("初始化会话, machineId: {}", machineId);

        try {
            // 访问网关，触发 OAuth 重定向，获取初始 Cookie
            HttpResult result = httpClient.doGetWithManualRedirect(machineId, gatewayUrl, 15);

            if (CollectionUtils.isEmpty(result.getCookies())) {
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                        "初始化失败：未获取到Cookie", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
            }

            // 保存到设备初始化会话（临时存储）
            sessionCache.saveDeviceInitSession(machineId, result.getCookies());

            // 解析页面，提取表单 token
            Document doc = Jsoup.parse(result.getBody());

            ProxyInitVO vo = new ProxyInitVO();
            vo.setMachineId(machineId);
            vo.setFinalUrl(result.getFinalUrl());
            vo.setLt(extractInputValue(doc, "lt"));
            vo.setExecution(extractInputValue(doc, "execution"));
            vo.setAuthMethodIDs(extractInputValue(doc, "authMethodIDs"));

            // 调试用，上线后移除
            vo.setCookies(result.getCookies());

            log.info("会话初始化成功, machineId: {}, cookies: {}", machineId, result.getCookies().size());
            return vo;

        } catch (Exception e) {
            log.error("初始化会话失败", e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "初始化失败：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }

    // ==================== 2. 发送短信 ====================

    /**
     * 发送短信验证码
     * <p>
     * 使用设备初始化会话中的 Cookie 请求发送短信。
     * 此时 userId 仅用于告诉服务器发送给谁，尚未与会话绑定。
     * </p>
     *
     * @param machineId 设备唯一标识
     * @param userId    学号/工号
     * @return 发送是否成功
     */
    @Override
    public boolean sendSms(String machineId, String userId) {
        log.info("发送短信, machineId: {}, userId: {}", machineId, userId);

        // 验证设备初始化会话存在
        validateDeviceInitSession(machineId);

        // 恢复初始化 Cookie 到 HttpClient
        restoreDeviceInitCookies(machineId);

        try {
            Map<String, String> formData = new HashMap<>();
            formData.put("j_username", CharacterConverter.toSBC(userId));

            log.debug("发送短信参数: j_username={}", CharacterConverter.toSBC(userId));

            HttpResult result = httpClient.doPost(machineId, smsSendUrl, formData);

            // 更新设备初始化 Cookie（服务器可能返回新 Cookie）
            if (!CollectionUtils.isEmpty(result.getCookies())) {
                sessionCache.updateDeviceInitCookies(machineId, result.getCookies());
            }

            boolean success = parseSmsResponse(result);
            log.info("短信发送{}, machineId: {}, userId: {}", success ? "成功" : "失败", machineId, userId);
            return success;

        } catch (IOException e) {
            log.error("发送短信失败", e);
            return false;
        }
    }

    /**
     * 解析短信发送响应
     */
    private boolean parseSmsResponse(HttpResult result) {
        if (!result.isSuccess()) return false;

        String body = result.getBody();
        if (!StringUtils.hasText(body)) return false;

        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode jsonNode = mapper.readTree(body);

            if (jsonNode.has("message")) {
                String message = jsonNode.get("message").asText();
                if ("I18NMessage.sendSMSCheckCodeSuccessmsg".equals(message) ||
                        message.contains("发送成功") ||
                        message.contains("success")) {
                    return true;
                }
            }
            return false;
        } catch (Exception e) {
            log.debug("响应不是JSON格式，使用字符串匹配");
            return false;
        }
    }

    // ==================== 3. 登录 ====================

    /**
     * 用户登录
     * <p>
     * 使用设备初始化 Cookie 进行登录验证。
     * 登录成功后，创建用户会话，绑定 machineId 和 userId。
     * </p>
     *
     * @param command 登录命令，包含 machineId、userId、验证码等
     * @return 登录结果
     */
    @Override
    public ProxyLoginResultVO login(ProxyLoginCommand command) {
        String machineId = command.getMachineId();
        String userId = command.getUserId();

        log.info("登录, machineId: {}, userId: {}, type: {}", machineId, userId, command.getLoginType());

        // 验证设备初始化会话存在
        validateDeviceInitSession(machineId);

        // 恢复初始化 Cookie 到 HttpClient
        restoreDeviceInitCookies(machineId);

        try {
            Map<String, String> formData = buildLoginFormData(command);
            HttpResult result = httpClient.doPost(machineId, loginUrl + "?sf_request_type=ajax", formData);

            // 检查是否需要图形验证码
            if (result.getBody().contains("j_checkcodeImgCode") || result.getBody().contains("验证码")) {
                log.warn("需要图形验证码");
                return ProxyLoginResultVO.builder()
                    .success(false)
                    .isNeedCaptcha(true)
                    .message("需要图形验证码")
                    .build();
            }
            // 判断登录结果
            boolean success = isLoginSuccess(result);

            if (success) {
                // 登录成功：创建用户会话
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
                String errorMsg = extractErrorMessage(result.getBody());
                log.warn("登录失败: {}", errorMsg);

                return ProxyLoginResultVO.builder()
                    .success(false)
                    .message(errorMsg)
                    .build();
            }
        } catch (IOException e) {
            log.error("登录请求失败", e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "登录请求失败：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }

    /**
     * 判断登录是否成功
     */
    private boolean isLoginSuccess(HttpResult result) {
        // 登录成功通常会重定向或返回特定内容
        String body = result.getBody();

        // 检查是否包含成功标志
        if (body.contains("success") || body.contains("登录成功")) {
            return true;
        }

        // 检查是否被重定向到目标页面（非登录页）
        if (result.getFinalUrl() != null && !result.getFinalUrl().contains("login")) {
            return true;
        }

        // 检查 JSON 响应
        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode json = mapper.readTree(body);
            if (json.has("status") && "success".equals(json.get("status").asText())) {
                return true;
            }
        } catch (Exception ignored) {
        }

        return false;
    }

    // ==================== 4. 代理访问 API ====================

    /**
     * 代理访问学校 API
     * <p>
     * 使用用户登录会话中的 Cookie 访问学校内部 API。
     * 必须提供 machineId 和 userId 来定位正确的会话。
     * </p>
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     * @param apiUrl    目标 API URL
     * @return API 响应内容
     */
    public String proxyApi(String machineId, String userId, String apiUrl) {
        log.debug("代理API, machineId: {}, userId: {}, url: {}", machineId, userId, apiUrl);

        // 验证用户会话存在
        validateUserSession(machineId, userId);

        // 恢复用户 Cookie 到 HttpClient
        restoreUserSessionCookies(machineId, userId);

        try {
            HttpResult result = httpClient.doGet(machineId, apiUrl);

            // 检查是否被重定向到登录页（Session 过期）
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

    /**
     * 代理访问 API（使用当前活跃账号）
     * <p>便捷方法，自动使用设备当前活跃账号</p>
     *
     * @param machineId 设备唯一标识
     * @param apiUrl    目标 API URL
     * @return API 响应内容
     */
    @Override
    public String proxyApi(String machineId, String apiUrl) {
        String userId = sessionCache.getActiveAccount(machineId);
        if (userId == null) {
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "未登录，请先登录", ResultCodeEnum.UNAUTHORIZED.getCode());
        }
        return proxyApi(machineId, userId, apiUrl);
    }

    // ==================== 5. 检查会话 ====================

    /**
     * 检查用户会话是否有效
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     * @return true 如果会话有效
     */
    public boolean checkSession(String machineId, String userId) {
        if (!sessionCache.hasUserSession(machineId, userId)) {
            return false;
        }

        // 尝试访问网关验证会话
        try {
            restoreUserSessionCookies(machineId, userId);
            HttpResult result = httpClient.doGet(machineId, gatewayUrl);

            boolean valid = result.getFinalUrl() == null || !result.getFinalUrl().contains("login");

            if (!valid) {
                sessionCache.removeUserSession(machineId, userId);
            }

            return valid;
        } catch (IOException e) {
            return false;
        }
    }

    /**
     * 检查设备当前活跃会话是否有效
     *
     * @param machineId 设备唯一标识
     * @return true 如果会话有效
     */
    @Override
    public boolean checkSession(String machineId) {
        String userId = sessionCache.getActiveAccount(machineId);
        if (userId == null) {
            // 没有活跃用户，检查是否有初始化会话
            return sessionCache.hasDeviceInitSession(machineId);
        }
        return checkSession(machineId, userId);
    }

    // ==================== 6. 登出 ====================

    /**
     * 用户登出
     *
     * @param machineId 设备唯一标识
     * @param userId    用户ID
     */
    public void logout(String machineId, String userId) {
        log.info("登出, machineId: {}, userId: {}", machineId, userId);
        httpClient.clearUserCookies(machineId);
        sessionCache.removeUserSession(machineId, userId);
    }

    /**
     * 登出当前活跃账号
     *
     * @param machineId 设备唯一标识
     */
    @Override
    public void logout(String machineId) {
        String userId = sessionCache.getActiveAccount(machineId);
        if (userId != null) {
            logout(machineId, userId);
        } else {
            // 清理初始化会话
            sessionCache.removeDeviceInitSession(machineId);
        }
        httpClient.clearUserCookies(machineId);
    }

    // ==================== 7. 账号管理 ====================

    /**
     * 获取设备上所有已登录账号
     *
     * @param machineId 设备唯一标识
     * @return 用户ID 集合
     */
    public Set<String> getDeviceAccounts(String machineId) {
        return sessionCache.getValidDeviceAccounts(machineId);
    }

    /**
     * 获取设备当前活跃账号
     *
     * @param machineId 设备唯一标识
     * @return 当前活跃的用户ID
     */
    public String getActiveAccount(String machineId) {
        return sessionCache.getActiveAccount(machineId);
    }

    /**
     * 切换账号
     *
     * @param machineId 设备唯一标识
     * @param userId    目标用户ID
     * @return true 如果切换成功
     */
    public boolean switchAccount(String machineId, String userId) {
        return sessionCache.switchAccount(machineId, userId);
    }

    // ==================== 辅助方法 ====================

    /**
     * 验证设备初始化会话存在
     */
    private void validateDeviceInitSession(String machineId) {
        if (!sessionCache.hasDeviceInitSession(machineId)) {
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "会话不存在或已过期，请重新初始化", ResultCodeEnum.UNAUTHORIZED.getCode());
        }
    }

    /**
     * 验证用户会话存在
     */
    private void validateUserSession(String machineId, String userId) {
        if (!sessionCache.hasUserSession(machineId, userId)) {
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "未登录或会话已过期，请重新登录", ResultCodeEnum.UNAUTHORIZED.getCode());
        }
    }

    /**
     * 从缓存恢复设备初始化 Cookie 到 HttpClient
     */
    private void restoreDeviceInitCookies(String machineId) {
        List<Cookie> cookies = sessionCache.getDeviceInitCookies(machineId);
        if (!CollectionUtils.isEmpty(cookies)) {
            httpClient.clearUserCookies(machineId);
            httpClient.addCookies(machineId, cookies);
        }
    }

    /**
     * 从缓存恢复用户会话 Cookie 到 HttpClient
     */
    private void restoreUserSessionCookies(String machineId, String userId) {
        List<Cookie> cookies = sessionCache.getUserSessionCookies(machineId, userId);
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
                formData.put("j_username", command.getUserId());
                formData.put("sms_checkcode", command.getCode());
                formData.put("j_checkcode", "验证码");
                formData.put("op", "login");
                formData.put("spAuthChainCode", "3c21e7d55f6449df85e8cebc30518464");
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
    @SuppressWarnings("unused")
    @Deprecated
    private void randomDelay() {
        try {
            long delay = ThreadLocalRandom.current().nextLong(300, 1000);
            Thread.sleep(delay);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}