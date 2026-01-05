package cn.edu.sztui.common.cache.util.config;

import lombok.Data;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Data
@Configuration
public class SztuConfig {
    @Value("${sztu.constant.projectOrBrandName}")
    private String projectOrBrandName;
    @Value("${sztu.constant.projectOrBrandCode}")
    private String projectOrBrandCode;
    @Value("${sztu.constant.projectName:}")
    private String projectName;
    @Value("${sztu.constant.environment}")
    private String environment;
}
