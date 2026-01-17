package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthService;
import cn.edu.sztui.base.application.vo.LoginBasicResultVO;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import cn.edu.sztui.base.infrastructure.convertor.CharacterConverter;
import cn.edu.sztui.base.infrastructure.convertor.CookieConverter;
import cn.edu.sztui.base.infrastructure.util.browserpool.PlaywrightBrowserPool;
import cn.edu.sztui.base.infrastructure.util.cache.AuthSessionCacheUtil;
import cn.edu.sztui.base.infrastructure.util.cache.dto.ProxySession;
import cn.edu.sztui.base.infrastructure.util.ocr.CaptchaOcrUtil;
import cn.edu.sztui.base.infrastructure.wx.WxMaUserService;
import cn.edu.sztui.common.util.auth.UserContext;
import cn.edu.sztui.common.util.bean.TokenMessage;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import com.microsoft.playwright.options.Cookie;
import com.microsoft.playwright.options.FormData;
import com.microsoft.playwright.options.RequestOptions;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.Objects;

import static cn.edu.sztui.base.domain.model.SchoolAPIs.*;

@Slf4j
@Service
public class AuthServiceImpl implements AuthService {

    @Resource
    private PlaywrightBrowserPool browserPool;
    @Resource
    private AuthSessionCacheUtil authSessionCacheUtil;
    @Resource
    private CaptchaOcrUtil captchaOcrUtil;
    @Resource
    private WxMaUserService wxMaUserService;
    @Autowired
    private ObjectMapper  objectMapper;

    /**
     * 检测小程序账号的cookie活性
     *
     * @param tempCode
     * @return
     */
    @Override
    public boolean getSessionStatus(String tempCode) {
        TokenMessage tokenmesage = UserContext.getContext();
        String unionID = tokenmesage.getUnionId();
        return authSessionCacheUtil.hasSession(unionID);
    }

    @Override
    public LoginResultsVo init(String tempCode) {
        String unionID = wxMaUserService.login(tempCode).getUnionid();
        return refreshingCookies(unionID, authSessionCacheUtil.getSession(unionID));
    }

    private LoginResultsVo refreshingCookies(String tempCode, ProxySession session) {
        return browserPool.executeWithContext(context -> {
            String unionID = wxMaUserService.login(tempCode).getUnionid();
            boolean isUpdated = false;
            if (!Objects.isNull(session)) {
                context.addCookies(CookieConverter.fromCookieDTOs(session.getCookiesJson()));
                isUpdated = true;
            }
            // 访问登录页面
            LoginResultsVo ret = new LoginResultsVo();
            try {
                Page page = context.newPage();
                // page.navigate(gatewayStartURL);
                // page.waitForURL(gatewayEndURL);
                Response response = page.waitForResponse(
                        resp -> resp.url().equals(gatewayFirstEndURL) || resp.url().equals(gatewaySecondEndURL),
                        () -> page.navigate(gatewayStartURL)  // 这是在等待期间执行的动作
                );
                if( response.url().equals(gatewayFirstEndURL) ){
                    ret.setLoginTypes(Collections.singletonList(LoginType.SMS));
                }else{
                    List<LoginType> typeLists = Collections.singletonList(LoginType.SMS);
                    typeLists.add(LoginType.PASSWORD);
                    ret.setLoginTypes(typeLists);
                }
                ret.setMessage(response.text());
                // TODO 以后返回签发的token或者其他东西，返回cookie不安全
                ret.setCookies(context.cookies());
            } catch (Exception e) {
                log.error("会话初始化出现错误：" + e.getMessage());
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "会话初始化出现错误：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
            }
            if (isUpdated) authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            else authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            return ret;
        });
    }

    @Override
    public LoginResultsVo getSms(String tempCode, String usrId) {
        return browserPool.executeWithContext(context -> {
            String unionID = wxMaUserService.login(tempCode).getUnionid();
            // 缓存检测
            if (authSessionCacheUtil.hasSession(unionID)) {
                ProxySession session = authSessionCacheUtil.getSession(unionID);
                List<Cookie> preCookies = CookieConverter.fromCookieDTOs(session.getCookiesJson());
                context.addCookies(preCookies);
            }
            // 访问登录页面
            APIRequestContext req = context.request();
            // 重要！必须是表单形式
            FormData formData = FormData.create();
            formData.set("j_username", CharacterConverter.toSBC(usrId));
            // formData.put("j_authMethodID", "41");
            APIResponse res = req.post(smsURL+ "?sf_request_type=ajax",
                RequestOptions.create()
                .setForm(formData)
                .setHeader("X-Requested-With", "XMLHttpRequest")
                .setHeader("Accept", "application/json, text/javascript, */*; q=0.01")
                .setHeader("Referer", gatewayFirstEndURL)
                .setHeader("Origin", extractOrigin(smsURL))
                .setHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0")
            );

            // log.info("SMS请求URL: {}", smsURL);
            // log.info("SMS请求状态: {}", res.status());
            // log.info("SMS响应头: {}", res.headers());
            // log.info("SMS响应体: {}", res.text());

            // FIXME 如何确保 webvpn的cookie到账？
            authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            LoginResultsVo ret = new LoginResultsVo();
            ret.setMessage(res.text());
            ret.setCookies(context.cookies());
            return ret;
        });
    }

    // 辅助方法：提取 Origin
    private String extractOrigin(String url) {
        try {
            java.net.URL u = new java.net.URL(url);
            return u.getProtocol() + "://" + u.getHost() +
                    (u.getPort() != -1 ? ":" + u.getPort() : "");
        } catch (Exception e) {
            return "";
        }
    }

    public LoginBasicResultVO loginFrame(LoginRequestCommand cmd) {
        return browserPool.executeWithContext(context -> {
            String unionID = wxMaUserService.login(cmd.getWxCode()).getUnionid();
            LoginBasicResultVO ret = new LoginBasicResultVO();
            if (authSessionCacheUtil.hasSession(unionID)) {
                // 缓存检测
                ProxySession session = authSessionCacheUtil.getSession(unionID);
                List<Cookie> preCookies = CookieConverter.fromCookieDTOs(session.getCookiesJson());
                context.addCookies(preCookies);
            }

            // ============ 第一步：AJAX 验证 ============
            // 访问登录页面
            FormData ajaxData = FormData.create();
            ajaxData.set("j_username", CharacterConverter.toSBC(cmd.getUserId()));
            ajaxData.set("sms_checkcode",cmd.getSmsCode());
            ajaxData.set("j_checkcode","验证码");
            ajaxData.set("op","login");
            ajaxData.set("spAuthChainCode",spAuthChainCode);

            APIRequestContext req = context.request();
            APIResponse ajaxRes = req.post(loginURL+ "?sf_request_type=ajax",
                RequestOptions.create()
                    .setForm(ajaxData)
                    .setHeader("X-Requested-With", "XMLHttpRequest")
                    .setHeader("Referer", gatewayFirstEndURL)
                    .setHeader("Origin", extractOrigin(loginURL))  // 注意这里应该是loginURL的origin
                    .setHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0")
                    .setHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
                    .setHeader("Accept", "*/*")
            );
            String ajaxBody = ajaxRes.text();
            log.info("AJAX验证响应: {}", ajaxBody); // 一般是响应 {"loginFailed":"false"}
            // jackson 库中的核心类
            JsonNode json = objectMapper.readTree(ajaxBody);
            boolean loginFailed = json.path("loginFailed").asBoolean(true);

            if (loginFailed)
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "登录验证失败: " + ajaxBody, ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());

            // ============ 第二步：模拟表单提交（处理重定向链） ============

            // 如果重定向都是 HTTP 302，只用 API？
            APIResponse formRes = req.post(
                A4tLoginFormActionURL,
                RequestOptions.create()
                    .setForm(ajaxData)
                    .setHeader("Referer", gatewayFirstEndURL)
                    .setHeader("X-Requested-With", "XMLHttpRequest")
                    .setHeader("Origin", extractOrigin(loginURL))
                    .setHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0")
            );
            log.info("表单提交状态: {}", formRes.status());
            log.info("表单提交后 cookies: {}", context.cookies());
            // FIXME 等待登录的成功
            // ============ 更新cookie，完成登录  ============
            authSessionCacheUtil.sessionLoginBind(unionID, cmd.getUserId(), context.cookies());
            ret.setCookies(context.cookies());
            return ret;
        });
    }

    @Override
    public LoginResultsVo logout(LoginRequestCommand cmd) {
        return browserPool.executeWithContext(context -> {
            String unionID = wxMaUserService.login(cmd.getWxCode()).getUnionid();
            // 缓存检测
            if (authSessionCacheUtil.hasSession(unionID)) {
                ProxySession session = authSessionCacheUtil.getSession(unionID);
                List<Cookie> preCookies = CookieConverter.fromCookieDTOs(session.getCookiesJson());
                context.addCookies(preCookies);
            }
            // 访问登录页面
            APIRequestContext req = context.request();
            APIResponse res = req.get(logoutURL);
            log.info("退出响应:{} {}", res.status(),res.text());
            
            authSessionCacheUtil.sessionLogoutBind( unionID );
            LoginResultsVo ret = new LoginResultsVo();
            ret.setCookies(context.cookies());
            return ret;
        });
    }
}
