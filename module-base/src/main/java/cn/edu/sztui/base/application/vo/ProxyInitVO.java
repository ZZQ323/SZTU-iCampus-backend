package cn.edu.sztui.base.application.vo;

import lombok.Data;
import org.apache.http.cookie.Cookie;

import java.util.List;

/**
 * 代理初始化结果
 */
@Data
public class ProxyInitVO {

    /**
     * 机器ID（后续请求必须携带）
     */
    private String machineId;

    /**
     * 最终URL
     */
    private String finalUrl;

    /**
     * 表单token（登录时需要）
     */
    private String lt;
    private String execution;
    private String authMethodIDs;
    // 仅调试
    private List<Cookie> cookies;
}