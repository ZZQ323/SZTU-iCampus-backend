package cn.edu.sztui.base.domain.model.loginhandle;

import com.microsoft.playwright.Page;


public interface LoginHandle {

    void login(Page page, LoginType type, String userId, String code);
}
