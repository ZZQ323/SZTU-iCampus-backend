package cn.edu.sztui.base.domain.model.wxmini;

import cn.binarywang.wx.miniapp.api.WxMaService;
import cn.binarywang.wx.miniapp.bean.WxMaJscode2SessionResult;
import cn.binarywang.wx.miniapp.bean.WxMaPhoneNumberInfo;
import cn.binarywang.wx.miniapp.bean.WxMaUserInfo;
import cn.binarywang.wx.miniapp.util.WxMaConfigHolder;
import cn.edu.sztui.base.infrastructure.util.JsonUtils;
import cn.edu.sztui.base.infrastructure.wx.WxminiConfiguration;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import me.chanjar.weixin.common.error.WxErrorException;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.DigestUtils;
import org.springframework.util.StringUtils;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * 微小专用设备标识（待测试！）
 */
@Slf4j
@Service
public class WechatDeviceServiceImpl {

    @Resource
    private RedisTemplate<String, Object> redisTemplate;
    @Resource
    private WxminiConfiguration wxminiConfiguration;
    @Resource
    private  WxMaService wxMaService;

    /**
     * 微信小程序获取设备唯一标识
     * 使用微信的 openid + deviceToken 作为组合标识
     */
    public String getWechatDeviceId(String code,String deviceToken) {
        if (StringUtils.isEmpty(deviceToken)) {
            // 首次使用，获取设备信息
            deviceToken = login(wxminiConfiguration.getAppid(),code);
        }
        // 组合标识：openid + deviceToken 的哈希
        String combined = code + "|" + deviceToken;
        // md5 对称加密
        String deviceId = "wechat_" + DigestUtils.md5DigestAsHex(combined.getBytes());

        // 缓存设备信息
        String key = "device:wechat:" + deviceId;
        Map<String, Object> deviceInfo = new HashMap<>();
        deviceInfo.put("code", code);
        deviceInfo.put("deviceToken", deviceToken);
        deviceInfo.put("lastActive", System.currentTimeMillis());

        redisTemplate.opsForHash().putAll(key, deviceInfo);
        redisTemplate.expire(key, 90, TimeUnit.DAYS);
        return deviceId;
    }

    /**
     * 登陆接口
     */
    public String login(String appid, String code) {
        if (org.apache.commons.lang3.StringUtils.isBlank(code)) {
            return "empty jscode";
        }

        if (!wxMaService.switchover(appid)) {
            throw new IllegalArgumentException(String.format("未找到对应appid=[%s]的配置，请核实！", appid));
        }

        try {
            WxMaJscode2SessionResult session = wxMaService.getUserService().getSessionInfo(code);
            log.info(session.getSessionKey());
            log.info(session.getOpenid());
            //TODO 可以增加自己的逻辑，关联业务相关数据
            return JsonUtils.toJson(session);
        } catch (WxErrorException e) {
            log.error(e.getMessage(), e);
            return e.toString();
        } finally {
            WxMaConfigHolder.remove();//清理ThreadLocal
        }
    }

    /**
     * 获取用户信息接口
     */
    public String info(String appid, String sessionKey,String signature, String rawData, String encryptedData, String iv) {
        if (!wxMaService.switchover(appid)) {
            throw new IllegalArgumentException(String.format("未找到对应appid=[%s]的配置，请核实！", appid));
        }
        // 用户信息校验
        if (!wxMaService.getUserService().checkUserInfo(sessionKey, rawData, signature)) {
            WxMaConfigHolder.remove();//清理ThreadLocal
            return "user check failed";
        }

        // 解密用户信息
        WxMaUserInfo userInfo = wxMaService.getUserService().getUserInfo(sessionKey, encryptedData, iv);
        WxMaConfigHolder.remove();//清理ThreadLocal
        return JsonUtils.toJson(userInfo);
    }

    /**
     * 获取用户绑定手机号信息
     */
    public String phone(String appid, String sessionKey, String signature,String rawData, String encryptedData, String iv) {
        if (!wxMaService.switchover(appid)) {
            throw new IllegalArgumentException(String.format("未找到对应appid=[%s]的配置，请核实！", appid));
        }
        // 用户信息校验
        if (!wxMaService.getUserService().checkUserInfo(sessionKey, rawData, signature)) {
            WxMaConfigHolder.remove();//清理ThreadLocal
            return "user check failed";
        }
        // 解密
        WxMaPhoneNumberInfo phoneNoInfo = wxMaService.getUserService().getPhoneNoInfo(sessionKey, encryptedData, iv);
        WxMaConfigHolder.remove();//清理ThreadLocal
        return JsonUtils.toJson(phoneNoInfo);
    }
}
