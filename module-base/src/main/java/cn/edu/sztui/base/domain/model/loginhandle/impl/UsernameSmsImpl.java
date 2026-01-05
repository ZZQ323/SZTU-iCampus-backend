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

import java.util.concurrent.TimeUnit;

@Slf4j
@Service
public class UsernameSmsImpl implements LoginHandle {

    @Override
    public void login(Page page, LoginType type, String userId, String code) {
        if (StringUtils.isEmpty(userId))
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "账号缺失无法登录！", ResultCodeEnum.FORBIDDEN.getCode());
        if (StringUtils.isEmpty(code))
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "验证码缺失无法登录！", ResultCodeEnum.FORBIDDEN.getCode());

        page.waitForSelector("#" + LoginType.SMS.getConfig().getUsernameInputId());
        page.waitForSelector("#" + LoginType.SMS.getConfig().getSmsInputId());
        try {
            Locator usernameInput = page.locator("#" + LoginType.SMS.getConfig().getUsernameInputId());
            usernameInput.clear();
            usernameInput.fill(userId);
            Locator codeInput = page.locator("#" + LoginType.SMS.getConfig().getSmsInputId());
            codeInput.clear();
            codeInput.fill(code);
            page.locator("#" + LoginType.SMS.getConfig().getLoginButtonId()).click();
            // TimeUnit.SECONDS.sleep(12);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "爬虫无法进行账号密码登录！！", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        }
    }
}
