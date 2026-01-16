package cn.edu.sztui.base.domain.model.loginhandle.impl;

import cn.edu.sztui.base.domain.model.loginhandle.LoginHandle;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import com.microsoft.playwright.Page;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class UsernamePasswordImpl implements LoginHandle {

    @Override
    public void login(Page page, LoginType type, String userId, String code) {

    }
}
