package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.infrastructure.convertor.CookieConverter;
import cn.edu.sztui.base.infrastructure.util.browserpool.PlaywrightBrowserPool;
import cn.edu.sztui.base.infrastructure.util.cache.AuthSessionCacheUtil;
import cn.edu.sztui.base.infrastructure.util.cache.dto.ProxySession;
import cn.edu.sztui.base.infrastructure.util.ocr.CaptchaOcrUtil;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.LoadState;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.util.Objects;
import static cn.edu.sztui.base.domain.model.SchoolAPIs.gatewayURL;
import static cn.edu.sztui.base.domain.model.SchoolAPIs.smsURL;

@Slf4j
@Service
public class AuthServiceImpl implements AuthService {

    @Resource
    private PlaywrightBrowserPool browserPool;
    @Resource
    private AuthSessionCacheUtil authSessionCacheUtil;
    @Resource
    private CaptchaOcrUtil captchaOcrUtil;

    @Override
    public LoginResultsVo init(String tempCode) {
        return refreshingCookies(tempCode,null);
    }

    @Override
    public LoginResultsVo refresh(String tempCode) {
        // TODO 用 tempCode 换到 openid
        String openid = tempCode;
        return refreshingCookies(tempCode,authSessionCacheUtil.getMachineSession());
    }

    private LoginResultsVo refreshingCookies(String code, ProxySession session){
        return browserPool.executeWithContext(context -> {
            // 统一初始化与更新cookie的事情
            // 一共四种情况，但是都在 ProxySession 里面有表示的！
            //  未初始化（走流程）
            //  初始化过期（redis消失，走流程）
            //  绑定用户有效期中（走流程）
            //  绑定用户有效期过期（redis消失）
            // TODO 待测试
            boolean isUpdated = false;
            if(!Objects.isNull(session)){
                context.addCookies(CookieConverter.fromCookieDTOs(session.getCookiesJson()));
                isUpdated =  true;
            }
            // 访问登录页面
            APIRequestContext req = context.request();
            APIResponse res = null;
            LoginResultsVo ret = new LoginResultsVo();
            try {
                res = req.get(gatewayURL);
                if(isUpdated)authSessionCacheUtil.updateSessionCookies(code,context.cookies());
                else authSessionCacheUtil.saveInitialSession(code,context.cookies());
                // TODO 以后返回签发的token或者其他东西，返回cookie不安全
                ret.setCookies(context.cookies());
            } catch (Exception e) {
                log.error("初始化出现错误："+e.getMessage());
            }
            return ret;
        });
    }

    @Override
    public LoginResultsVo getSms(String id){
        return browserPool.executeWithContext(context -> {
            Page page = context.newPage();
            // TODO 缓存检测
            // if (authSessionCacheUtil.hasValidSession(id)) {
            //     List<Cookie> cookies = authSessionCacheUtil.getCookies(id);
            //     context.addCookies(cookies);
            // }

            // 访问登录页面
            APIRequestContext req = context.request();
            APIResponse res;
            // page.navigate(gatewayURL);
            // FIXME 等待webvpn的cookie到账
            // page.waitForLoadState(LoadState.LOAD);
            // page.waitForLoadState(LoadState.DOMCONTENTLOADED);
            // page.waitForLoadState(LoadState.NETWORKIDLE);
            res = req.get(gatewayURL);
            // 请求登录URL，自动处理跳转
            res = req.post(smsURL);

            // FIXME 等待webvpn的cookie到账
            page.waitForLoadState(LoadState.LOAD);
            page.waitForLoadState(LoadState.DOMCONTENTLOADED);
            page.waitForLoadState(LoadState.NETWORKIDLE);

            // TODO 缓存save <code,usrid,cookies> - expiray ，但是不知道知道save什么

            LoginResultsVo ret = new LoginResultsVo();
            return ret;
        });
    }

    public LoginResultsVo loginFrame(LoginRequestCommand cmd){
        // TODO
        return null;
    }


}
