package cn.edu.sztui.base.web;

import cn.binarywang.wx.miniapp.api.WxMaService;
import cn.binarywang.wx.miniapp.bean.WxMaJscode2SessionResult;
import cn.binarywang.wx.miniapp.util.WxMaConfigHolder;
import cn.edu.sztui.base.application.dto.command.WXLoginDTO;
import cn.edu.sztui.base.application.vo.TokenAuthVo;
import cn.edu.sztui.common.util.auth.UserContext;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import cn.edu.sztui.common.util.jwt.JwtConfig;
import cn.edu.sztui.common.util.result.Result;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import me.chanjar.weixin.common.error.WxErrorException;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.util.Objects;

@Slf4j
@RestController
@RequestMapping("/wx-auth")
public class WxAuthController {
    @Resource
    private WxMaService wxMaService;
    @Autowired
    private JwtConfig jwtConfig;

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

    /**
     * 检验token是否过期
     */
    @GetMapping("/v1/active")
    public Result isActive() {
        log.info("用户 {} 进行验证", UserContext.getContext());
        return Result.ok(Objects.isNull(UserContext.getContext())?false:true);
    }

    /**
     * <p>小程序登录 - 首次需要调用</p>
     * <p>刷新 token - 快过期时调用</p>
     */
    @PostMapping("/v1/get-token")
    public Result getToken(@RequestBody WXLoginDTO dto) {
        if (StringUtils.isBlank(dto.getWxCode()))throw new BusinessException(SysReturnCode.WECHAT_PROXY.getCode(),  "empty jscode", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        if ( !wxMaService.switchover(appid) )throw new BusinessException(SysReturnCode.WECHAT_PROXY.getCode(), String.format("未找到对应appid=[%s]的配置，请核实！", appid), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        try {
            // 用 code 换取 openid（调用微信接口）
            WxMaJscode2SessionResult session = wxMaService.getUserService().getSessionInfo(dto.getWxCode());
            //  生成 JWT
            log.info("临时登录码{} ",dto.getWxCode());
            log.info("已经获得 SessionKey：{} 已经获得 Unionid：{} 已经获得 openId：{}",session.getSessionKey(),session.getUnionid(),session.getOpenid());
            // 返回 token（只做信息的转录）
            String token = jwtConfig.generateToken(session, 1 * 60 * 60);
            TokenAuthVo ret = new TokenAuthVo();
            ret.setToken(token);
            return Result.ok(ret);
        } catch (WxErrorException e) {
            log.error(e.getMessage(), e);
            throw new BusinessException(SysReturnCode.WECHAT_PROXY.getCode(), e.getMessage(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
        } finally {
            WxMaConfigHolder.remove();//清理ThreadLocal
        }
    }
}
