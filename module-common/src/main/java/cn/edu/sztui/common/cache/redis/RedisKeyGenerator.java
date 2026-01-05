package cn.edu.sztui.common.cache.redis;

import cn.edu.sztui.common.cache.util.config.SztuConfig;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Component;

@Component
public class RedisKeyGenerator {
    @Resource
    private SztuConfig sztuConfig;

    public String prefix() {
        return this.sztuConfig.getEnvironment() + ":" + this.sztuConfig.getProjectOrBrandName() + ":";
    }

    public String generate(String key) {
        return this.prefix() + key;
    }
}