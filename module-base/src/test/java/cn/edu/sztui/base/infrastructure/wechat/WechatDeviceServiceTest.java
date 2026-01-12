package cn.edu.sztui.base.infrastructure.wechat;


import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.HashOperations;
import org.springframework.data.redis.core.RedisTemplate;
import java.util.concurrent.TimeUnit;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;


@ExtendWith(MockitoExtension.class)
class WechatDeviceServiceTest {

    @Mock
    private RedisTemplate<String, Object> redisTemplate;

    @Mock
    private HashOperations<String, Object, Object> hashOperations;

    @InjectMocks
    private WechatDeviceService wechatDeviceService;

    @Test
    void testGetWechatDeviceId_WithDeviceToken() {
        // 准备测试数据
        String openid = "test_openid_123";
        String deviceToken = "device_token_456";

        // 模拟 Redis 行为
        when(redisTemplate.opsForHash()).thenReturn(hashOperations);

        // 执行测试
        String deviceId = wechatDeviceService.getWechatDeviceId(openid, deviceToken);

        // 验证结果
        assertNotNull(deviceId);
        assertTrue(deviceId.startsWith("wechat_"));
        assertEquals(32 + 6, deviceId.length()); // wechat_ + 32位MD5

        // 验证 Redis 操作
        verify(redisTemplate).opsForHash();
        verify(hashOperations).putAll(anyString(), anyMap());
        verify(redisTemplate).expire(anyString(), eq(90L), eq(TimeUnit.DAYS));
    }

    @Test
    void testGetWechatDeviceId_WithoutDeviceToken() {
        // 准备测试数据
        String openid = "test_openid_123";

        // 模拟 Redis 行为
        when(redisTemplate.opsForHash()).thenReturn(hashOperations);

        // 执行测试
        String deviceId = wechatDeviceService.getWechatDeviceId(openid, null);

        // 验证结果
        assertNotNull(deviceId);
        assertTrue(deviceId.startsWith("wechat_"));

        // 验证 Redis 操作
        verify(redisTemplate).opsForHash();
        verify(hashOperations).putAll(anyString(), anyMap());
        verify(redisTemplate).expire(anyString(), eq(90L), eq(TimeUnit.DAYS));
    }

    @Test
    void testGetWechatDeviceId_ConsistentResult() {
        // 准备测试数据
        String openid = "test_openid_123";
        String deviceToken = "device_token_456";

        when(redisTemplate.opsForHash()).thenReturn(hashOperations);

        // 多次调用应该返回相同的结果
        String deviceId1 = wechatDeviceService.getWechatDeviceId(openid, deviceToken);
        String deviceId2 = wechatDeviceService.getWechatDeviceId(openid, deviceToken);

        assertEquals(deviceId1, deviceId2);
    }
}
