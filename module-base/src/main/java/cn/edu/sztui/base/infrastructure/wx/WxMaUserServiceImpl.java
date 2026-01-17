package cn.edu.sztui.base.infrastructure.wx;

import cn.binarywang.wx.miniapp.api.WxMaService;
import cn.binarywang.wx.miniapp.bean.WxMaJscode2SessionResult;
import cn.binarywang.wx.miniapp.util.WxMaConfigHolder;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import me.chanjar.weixin.common.error.WxErrorException;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class WxMaUserServiceImpl implements WxMaUserService {
    @Resource
    private WxMaService wxMaService;

    @Value("${wx.miniapp.configs[0].appid}")
    private String appid;
    @Value("${wx.miniapp.configs[0].aesKey}")
    private String aesKey;
    @Value("${wx.miniapp.configs[0].secret}")
    private String secret;
    @Value("${wx.miniapp.configs[0].msgDataFormat}")
    private String msgDataFormat;
    @Value("${wx.miniapp.configs[0].rsaKey}")
    private String rsaKey;

    @Override
    public WxMaJscode2SessionResult login(String code) {
        if (StringUtils.isBlank(code))throw new BusinessException(SysReturnCode.WECHAT_PROXY.getCode(),  "empty jscode", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        if ( !wxMaService.switchover(appid) )throw new BusinessException(SysReturnCode.WECHAT_PROXY.getCode(), String.format("未找到对应appid=[%s]的配置，请核实！", appid), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        try {
            WxMaJscode2SessionResult session = wxMaService.getUserService().getSessionInfo(code);
            log.info("临时登录码{} 已经获得 SessionKey：{}",code,session.getSessionKey());
            log.info("临时登录码{} 已经获得 Unionid：{}",code,session.getUnionid());
            //TODO 可以增加自己的逻辑，关联业务相关数据
            return session;
        } catch (WxErrorException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(SysReturnCode.WECHAT_PROXY.getCode(), e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        } finally {
            WxMaConfigHolder.remove();//清理ThreadLocal
        }
    }
}
