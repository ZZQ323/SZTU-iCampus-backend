package cn.edu.sztui.base.domain.model.loginhandle;

import cn.edu.sztui.base.application.vo.LoginResultsVo;
import com.microsoft.playwright.Page;


public interface LoginHandle {
    final String loginURL ="https://home.sztu.edu.cn/bmportal";
    void login(Page page, LoginType type, String userId, String code);
}
