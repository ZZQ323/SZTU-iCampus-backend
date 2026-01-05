package cn.edu.sztui.base.domain.model.loginhandle.impl;

import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.loginhandle.LoginHandle;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.LoadState;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Slf4j
@Service
public class UsernamePasswordImpl implements LoginHandle {

    @Override
    public void login(Page page, LoginType type, String userId, String code) {
        if (StringUtils.isEmpty(userId))
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "账号缺失无法登录！", ResultCodeEnum.FORBIDDEN.getCode());
        if (StringUtils.isEmpty(code))
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "密码缺失无法登录！", ResultCodeEnum.FORBIDDEN.getCode());

        // 访问登录页面
        page.navigate(loginURL);
        // NETWORKIDLE 不等于 "JS 执行完"。需要等待目标元素可交互。
        page.waitForLoadState(LoadState.LOAD);
        page.waitForLoadState(LoadState.DOMCONTENTLOADED);
        page.waitForLoadState(LoadState.NETWORKIDLE);

        page.waitForSelector("input[id='" + LoginType.USERNAME_PASSWORD.getConfig().getUsernameInputId() + "']", new Page.WaitForSelectorOptions());
        page.waitForSelector("input[id='" + LoginType.USERNAME_PASSWORD.getConfig().getPasswordInputId() + "']", new Page.WaitForSelectorOptions());

        try {
            Locator usernameInput = page.locator("input[id='" + LoginType.USERNAME_PASSWORD.getConfig().getUsernameInputId() + "']");
            usernameInput.clear();
            usernameInput.fill(userId);
            Locator codeInput = page.locator("input[id='" + LoginType.USERNAME_PASSWORD.getConfig().getPasswordInputId() + "']");
            codeInput.clear();
            codeInput.fill(userId);
            page.locator("#" + LoginType.USERNAME_PASSWORD.getConfig().getLoginButtonId()).click();
            page.waitForLoadState(LoadState.LOAD);
            page.waitForLoadState(LoadState.DOMCONTENTLOADED);
            page.waitForLoadState(LoadState.NETWORKIDLE);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "爬虫无法进行账号密码登录！！", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }
}
