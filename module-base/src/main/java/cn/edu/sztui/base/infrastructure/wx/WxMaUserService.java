package cn.edu.sztui.base.infrastructure.wx;

import cn.binarywang.wx.miniapp.bean.WxMaJscode2SessionResult;

public interface WxMaUserService {
    WxMaJscode2SessionResult login(String code);
}
