package cn.edu.sztui.base.application.service.impl.proxy.auth;

import cn.edu.sztui.base.application.dto.command.ProxyLoginCommand;
import cn.edu.sztui.base.domain.model.proxy.SchoolHttpClient;
import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import cn.edu.sztui.base.infrastructure.constants.LoginType;
import cn.edu.sztui.base.infrastructure.persistence.CharacterConverter;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.Resource;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class SmsAuthService implements AuthService {

    @Resource
    private final SchoolHttpClient httpClient;
    @Resource
    private final ProxySessionCacheUtil sessionCache;
    @Resource
    private final ProxySessionCacheUtil proxySessionCacheUtil;

    @Value("${school.url.sms-send}")
    private String smsSendUrl;

    @Override
    public LoginType getSupportedType() {
        return LoginType.SMS;
    }

    @Override
    public Map<String, String> buildFormData(ProxyLoginCommand command) {
        Map<String, String> formData = new HashMap<>();
        formData.put("j_username", command.getUserId());
        formData.put("sms_checkcode", command.getCode());
        formData.put("j_checkcode", "验证码");
        formData.put("op", "login");
        formData.put("spAuthChainCode", "3c21e7d55f6449df85e8cebc30518464");
        return formData;
    }

    public boolean sendSms(String machineId, String userId) {
        log.info("发送短信, machineId: {}, userId: {}", machineId, userId);

        // cookieHelper.restoreDeviceInitCookies(machineId);

        try {
            Map<String, String> formData = new HashMap<>();
            formData.put("j_username", CharacterConverter.toSBC(userId));

            HttpResult result = httpClient.doPost(machineId, smsSendUrl, formData);

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

    private boolean parseSmsResponse(HttpResult result) {
        if (!result.isSuccess()) return false;

        String body = result.getBody();
        if (!StringUtils.hasText(body)) return false;

        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode jsonNode = mapper.readTree(body);
            if (jsonNode.has("message")) {
                String message = jsonNode.get("message").asText();
                return "I18NMessage.sendSMSCheckCodeSuccessmsg".equals(message)
                        || message.contains("发送成功")
                        || message.contains("success");
            }
        } catch (Exception e) {
            log.debug("响应不是JSON格式");
        }
        return false;
    }
}
