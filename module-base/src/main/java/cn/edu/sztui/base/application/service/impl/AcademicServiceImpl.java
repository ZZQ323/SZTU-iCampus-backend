package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.service.AcademicService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.infrastructure.convertor.CookieConverter;
import cn.edu.sztui.base.infrastructure.util.browserpool.PlaywrightBrowserPool;
import cn.edu.sztui.base.infrastructure.util.cache.AuthSessionCacheUtil;
import cn.edu.sztui.base.infrastructure.util.cache.dto.ProxySession;
import cn.edu.sztui.common.util.auth.UserContext;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import com.microsoft.playwright.options.Cookie;
import com.microsoft.playwright.options.FormData;
import com.microsoft.playwright.options.RequestOptions;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Objects;

import static cn.edu.sztui.base.domain.model.SchoolAPIs.*;

@Slf4j
@Service
public class AcademicServiceImpl implements AcademicService {

    @Resource
    private PlaywrightBrowserPool browserPool;
    @Resource
    private AuthSessionCacheUtil authSessionCacheUtil;

    @Override
    public LoginResultsVo init(String tempCode) {
        // TODO tokenmessage模块尚未测试
        String unionID = UserContext.getContext().getUnionId();
        return refreshingCookies(unionID, authSessionCacheUtil.getSession(unionID));
    }

    private LoginResultsVo refreshingCookies(String tempCode, ProxySession session) {
        return browserPool.executeWithContext(context -> {
            // TODO tokenmessage模块尚未测试
            String unionID = UserContext.getContext().getUnionId();
            boolean isUpdated = false;
            if (!Objects.isNull(session)) {
                context.addCookies(CookieConverter.fromCookieDTOs(session.getCookiesJson()));
                isUpdated = true;
            }
            // 访问登录页面
            LoginResultsVo ret = new LoginResultsVo();
            try {
                Page page = context.newPage();
                Response response = page.waitForResponse(
                        resp -> resp.url().equals(AASysSwitchPort) || resp.url().equals(AcdemAdminSysURL),
                        () -> page.navigate(AASysGatewayURL)  // 这是在等待期间执行的动作
                );
                if( response.url().equals(AASysSwitchPort) ){
                    // TODO 正是选课期间，可以进行礼貌的提醒
                    // ret.setLoginTypes(Collections.singletonList(LoginType.SMS));
                }
                // 然后其实就完成了
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
    public String getCrouseTable(){
        return browserPool.executeWithContext(context -> {
            // TODO tokenmessage模块尚未测试
            String unionID = UserContext.getContext().getUnionId();
            if (authSessionCacheUtil.hasSession(unionID)) {
                ProxySession session = authSessionCacheUtil.getSession(unionID);
                List<Cookie> preCookies = CookieConverter.fromCookieDTOs(session.getCookiesJson());
                context.addCookies(preCookies);
            }
            // 访问登录页面
            APIRequestContext req = context.request();
            // 重要！必须是表单形式
            FormData formData = FormData.create();
            // cj0701id=&zc=&demo=&xnxq01id=2024-2025-1&sfFD=1&wkbkc=1&kbjcmsid=EB5693B95B204102B2E28C5624C6E9ED
            // cj0701id=
            // zc=
            // demo=
            // xnxq01id=2024-2025-2
            // sfFD=1
            // wkbkc=1
            // kbjcmsid=EB5693B95B204102B2E28C5624C6E9ED
            // xstzd 显示通知单编号
            // xswk 显示网课群号及链接
            formData.set("cj0701id", "");   // 无意义
            formData.set("zc", "");         // 第几周
            formData.set("demo", "");       // 无意义
            formData.set("xnxq01id", "");   // 学年学期
            formData.set("sfFD","1");       // 是否放大
            formData.set("wkbkc", "1");     // 显示无课表课程
            formData.set("kbjcmsid", "");   // 时间模式
            APIResponse res = req.post(scheduleTableURL+ "?sf_request_type=ajax",
                RequestOptions.create()
                        .setForm(formData)
                        .setHeader("X-Requested-With", "XMLHttpRequest")
                        .setHeader("Accept", "application/json, text/javascript, */*; q=0.01")
                        .setHeader("Referer", gatewayFirstEndURL)
                        // .setHeader("Origin", extractOrigin(smsURL))
                        .setHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0")
            );
            authSessionCacheUtil.saveOrUpdateSession(unionID, context.cookies());
            return res.text();
        });
    }
}
