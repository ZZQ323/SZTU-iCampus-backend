package cn.edu.sztui.base.domain.model.loginhandle.impl;

import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.loginhandle.LoginHandle;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;


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
        Locator usernameInput = page.locator("#" + LoginType.SMS.getConfig().getUsernameInputId());
        usernameInput.clear();
        usernameInput.fill(userId);
        Locator codeInput = page.locator("#" + LoginType.SMS.getConfig().getSmsInputId());
        codeInput.clear();
        codeInput.fill(code);
        page.locator("#" + LoginType.SMS.getConfig().getLoginButtonId()).click();
    }
}
