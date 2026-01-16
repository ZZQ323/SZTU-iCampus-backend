package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.infrastructure.convertor.CharacterConverter;
import cn.edu.sztui.base.infrastructure.convertor.CookieConverter;
import cn.edu.sztui.base.infrastructure.util.browserpool.PlaywrightBrowserPool;
import cn.edu.sztui.base.infrastructure.util.cache.AuthSessionCacheUtil;
import cn.edu.sztui.base.infrastructure.util.cache.dto.ProxySession;
import cn.edu.sztui.base.infrastructure.util.ocr.CaptchaOcrUtil;
import cn.edu.sztui.base.infrastructure.wx.WxMaUserService;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import com.microsoft.playwright.options.Cookie;
import com.microsoft.playwright.options.RequestOptions;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
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

    /**
     * 检测小程序账号的cookie活性
     *
     * @param tempCode
     * @return
     */
    @Override
    public boolean getSessionStatus(String tempCode) {
        //        String unionID = wxMaUserService.login(tempCode).getUnionid();
        // TODO wx换unicode模块暂未测试
        String unionID = tempCode;
        return authSessionCacheUtil.hasSession(unionID);
    }

    @Override
    public LoginResultsVo init(String tempCode) {
//        String unionID = wxMaUserService.login(tempCode).getUnionid();
        // TODO wx换unicode模块暂未测试
        String unionID = tempCode;
        return refreshingCookies(unionID, null);
    }

    @Override
    public LoginResultsVo refresh(String tempCode) {
        // 用 tempCode 换到 unionID
//        String unionID = wxMaUserService.login(tempCode).getUnionid();
        // TODO wx换unicode模块暂未测试
        String unionID = tempCode;
        return refreshingCookies(unionID, authSessionCacheUtil.getSession(unionID));
    }

    private LoginResultsVo refreshingCookies(String tempCode, ProxySession session) {
        return browserPool.executeWithContext(context -> {
//            String unionID = wxMaUserService.login(tempCode).getUnionid();
            // TODO wx换unicode模块暂未测试
            String unionID = tempCode;
            boolean isUpdated = false;
            if (!Objects.isNull(session)) {
                context.addCookies(CookieConverter.fromCookieDTOs(session.getCookiesJson()));
                isUpdated = true;
            }
            // 访问登录页面
            try {
                Page page = context.newPage();
                // page.navigate(gatewayStartURL);
                // page.waitForURL(gatewayEndURL);
                Response response = page.waitForResponse(
                        resp -> resp.url().equals(gatewayEndURL),
                        () -> page.navigate(gatewayStartURL)  // 这是在等待期间执行的动作
                );
            } catch (Exception e) {
                log.error("会话初始化出现错误：" + e.getMessage());
                throw new BusinessException(SysReturnCode.WECHAT_PROXY.getCode(), "会话初始化出现错误：" + e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
            }

            LoginResultsVo ret = new LoginResultsVo();
            if (isUpdated) authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            else authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            // TODO 以后返回签发的token或者其他东西，返回cookie不安全
            ret.setCookies(context.cookies());
            return ret;
        });
    }

    @Override
    public LoginResultsVo getSms(String tempCode, String usrId) {
        return browserPool.executeWithContext(context -> {
            // 缓存检测
            // TODO wx换unicode模块暂未测试
//            String unionID = wxMaUserService.login(tempCode).getUnionid();
            String unionID = tempCode;
            if (authSessionCacheUtil.hasSession(unionID)) {
                ProxySession session = authSessionCacheUtil.getSession(unionID);
                List<Cookie> preCookies = CookieConverter.fromCookieDTOs(session.getCookiesJson());
                context.addCookies(preCookies);
            }
            // 访问登录页面
            APIRequestContext req = context.request();
            Map<String, Object> formData = new HashMap<>();
            formData.put("j_username", CharacterConverter.toSBC(usrId));
            APIResponse res = req.post(smsURL, RequestOptions
                    .create()
                    .setData(formData)
                    .setHeader("X-Requested-With", "XMLHttpRequest"));

            // FIXME 如何确保 webvpn的cookie到账？
            authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            LoginResultsVo ret = new LoginResultsVo();
            ret.setCookies(context.cookies());
            return ret;
        });
    }

    public LoginResultsVo loginFrame(LoginRequestCommand cmd) {
        // TODO
        return browserPool.executeWithContext(context -> {
            // 缓存检测
            // TODO wx换unicode模块暂未测试
//            String unionID = wxMaUserService.login(cmd.getWxCode()).getUnionid();
            String unionID = cmd.getWxCode();
            if (authSessionCacheUtil.hasSession(unionID)) {
                ProxySession session = authSessionCacheUtil.getSession(unionID);
                List<Cookie> preCookies = CookieConverter.fromCookieDTOs(session.getCookiesJson());
                context.addCookies(preCookies);
            }
            // 访问登录页面
            APIRequestContext req = context.request();
            APIResponse res = req.post(loginURL);
            // FIXME 如何确保 webvpn的cookie到账？
            authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            LoginResultsVo ret = new LoginResultsVo();
            ret.setCookies(context.cookies());
            return ret;
        });
    }

    @Override
    public LoginResultsVo logout(LoginRequestCommand cmd) {
        return browserPool.executeWithContext(context -> {
            // 缓存检测
            // TODO wx换unicode模块暂未测试
//            String unionID = wxMaUserService.login(cmd.getWxCode()).getUnionid();
            String unionID = cmd.getWxCode();
            if (authSessionCacheUtil.hasSession(unionID)) {
                ProxySession session = authSessionCacheUtil.getSession(unionID);
                List<Cookie> preCookies = CookieConverter.fromCookieDTOs(session.getCookiesJson());
                context.addCookies(preCookies);
            }
            // 访问登录页面
            APIRequestContext req = context.request();
            APIResponse res = req.get(logoutURL);
            // FIXME 如何确保 webvpn的cookie到账？
            authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            LoginResultsVo ret = new LoginResultsVo();
            ret.setCookies(context.cookies());
            return ret;
        });
    }
}
