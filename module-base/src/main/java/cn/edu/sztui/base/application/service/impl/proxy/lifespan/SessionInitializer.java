package cn.edu.sztui.base.application.service.impl.proxy.lifespan;

import cn.edu.sztui.base.application.vo.ProxyInitVO;
import cn.edu.sztui.base.domain.model.proxy.SchoolHttpClient;
import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import cn.edu.sztui.base.domain.model.proxy.parser.HtmlParser;
import cn.edu.sztui.base.infrastructure.util.cache.ProxySessionCacheUtil;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import jakarta.annotation.Resource;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.cookie.Cookie;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

import java.util.List;

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

            HttpResult result;
            // 先检查缓存中是否已存在有效session
            if( sessionCache.hasDeviceInitSession(machineId) ){
                // 如果有，则带上这些cookie去初始化
                log.info("会话已存在, machineId: {}, cookies: {}", machineId,sessionCache.getDeviceInitCookies(machineId) ); // 正式版需要注释掉
                List<Cookie> oldCookies = sessionCache.getDeviceInitCookies(machineId);
                result = httpClient.doGetWithManualRedirect(machineId, gatewayUrl, 15,oldCookies);
                if( !result.getCookies().equals(oldCookies) ){
                    // 触发覆盖
                    log.info("{} 的cookie 已更新 {} ====>>>  {}", machineId,oldCookies,result.getCookies() );
                    sessionCache.saveDeviceInitSession(machineId,result.getCookies());
                }
                log.info("会话初始化成功, machineId: {}, cookies: {}", machineId, result.getCookies());
            }else{
                result = httpClient.doGetWithManualRedirect(machineId, gatewayUrl, 15,null);
                if (CollectionUtils.isEmpty(result.getCookies()))
                    throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),"初始化失败：未获取到Cookie", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
                // log.info("添加前：{}",result.getCookies());
//                result.getCookies().add(new BasicClientCookie("x","x"));
                // log.info("添加后：{}",result.getCookies());
                sessionCache.saveDeviceInitSession(machineId,result.getCookies());
                // log.info("type of result.getCookies() is {}",result.getCookies().get(0).getClass().getSimpleName() );  :::: BasicClientCookie
                log.info("会话初始化成功, machineId: {}, cookies: {}", machineId, result.getCookies());
            }
            return setVo(machineId,result);
        } catch (Exception e) {
            log.error("初始化会话失败", e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),
                    "初始化失败：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }

    private ProxyInitVO setVo(String machineId,HttpResult result){
        Document doc = Jsoup.parse(result.getBody());
        ProxyInitVO vo = new ProxyInitVO();
        vo.setMachineId(machineId);
        vo.setFinalUrl(result.getFinalUrl());
        vo.setLt(htmlParser.extractInputValue(doc, "lt"));
        vo.setExecution(htmlParser.extractInputValue(doc, "execution"));
        vo.setAuthMethodIDs(htmlParser.extractInputValue(doc, "authMethodIDs"));
        vo.setCookies(result.getCookies());
        return vo;
    }
}