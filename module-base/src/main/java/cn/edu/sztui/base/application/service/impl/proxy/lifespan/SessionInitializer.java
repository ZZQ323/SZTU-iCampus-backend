package cn.edu.sztui.base.application.service.impl.proxy.lifespan;

import cn.edu.sztui.base.domain.model.proxy.parser.HtmlParser;
import cn.edu.sztui.base.application.vo.ProxyInitVO;
import cn.edu.sztui.base.domain.model.proxy.SchoolHttpClient;
import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import jakarta.annotation.Resource;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

@Slf4j
@Component
@RequiredArgsConstructor
public class SessionInitializer {
    @Resource
    private final SchoolHttpClient httpClient;
    @Resource
    private final ProxySessionCacheUtil sessionCache;
    @Resource
    private final HtmlParser htmlParser;

    @Value("${school.url.gateway}")
    private String gatewayUrl;

    public ProxyInitVO initSession(String machineId) {
        log.info("初始化会话, machineId: {}", machineId);
        try {
            HttpResult result = httpClient.doGetWithManualRedirect(machineId, gatewayUrl, 15);
            if (CollectionUtils.isEmpty(result.getCookies())) {
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                        "初始化失败：未获取到Cookie", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
            }
            sessionCache.saveDeviceInitSession(machineId, result.getCookies());
            Document doc = Jsoup.parse(result.getBody());
            ProxyInitVO vo = new ProxyInitVO();
            vo.setMachineId(machineId);
            vo.setFinalUrl(result.getFinalUrl());
            vo.setLt(htmlParser.extractInputValue(doc, "lt"));
            vo.setExecution(htmlParser.extractInputValue(doc, "execution"));
            vo.setAuthMethodIDs(htmlParser.extractInputValue(doc, "authMethodIDs"));
            vo.setCookies(result.getCookies());

            log.info("会话初始化成功, machineId: {}, cookies: {}", machineId, result.getCookies().size());
            return vo;

        } catch (Exception e) {
            log.error("初始化会话失败", e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "初始化失败：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }
}