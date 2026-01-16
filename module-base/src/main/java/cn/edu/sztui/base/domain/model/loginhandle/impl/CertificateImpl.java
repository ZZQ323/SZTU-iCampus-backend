package cn.edu.sztui.base.domain.model.loginhandle.impl;

import cn.edu.sztui.base.domain.model.loginhandle.LoginHandle;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import com.microsoft.playwright.Page;
import org.springframework.stereotype.Service;

@Service
public class CertificateImpl implements LoginHandle {

    @Override
    public void login(Page page, LoginType type, String userId, String code) {

    }
}
