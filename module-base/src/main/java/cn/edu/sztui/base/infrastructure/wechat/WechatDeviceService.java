package cn.edu.sztui.base.infrastructure.wechat;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.util.DigestUtils;
import org.springframework.util.StringUtils;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * 微小专用设备标识
 */
@Component
public class WechatDeviceService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    /**
     * 微信小程序获取设备唯一标识
     * 使用微信的 openid + deviceToken 作为组合标识
     */
    public String getWechatDeviceId(String openid, String deviceToken) {
        if (StringUtils.isEmpty(deviceToken)) {
            // 首次使用，获取设备信息
            deviceToken = requestDeviceTokenFromWechat();
        }

        // 组合标识：openid + deviceToken 的哈希
        String combined = openid + "|" + deviceToken;
        // md5 对称加密
        String deviceId = "wechat_" + DigestUtils.md5DigestAsHex(combined.getBytes());

        // 缓存设备信息
        String key = "device:wechat:" + deviceId;
        Map<String, Object> deviceInfo = new HashMap<>();
        deviceInfo.put("openid", openid);
        deviceInfo.put("deviceToken", deviceToken);
        deviceInfo.put("lastActive", System.currentTimeMillis());

        redisTemplate.opsForHash().putAll(key, deviceInfo);
        redisTemplate.expire(key, 90, TimeUnit.DAYS);
        return deviceId;
    }

    /**
     * 调用微信接口获取设备标识
     */
    private String requestDeviceTokenFromWechat() {
        // 微信获取设备信息的接口
        // wx.getSystemInfoSync() 获取设备信息
        // 或者使用 wx.getStorageSync('device_token') 如果之前存储过
        return UUID.randomUUID().toString();
    }
}
