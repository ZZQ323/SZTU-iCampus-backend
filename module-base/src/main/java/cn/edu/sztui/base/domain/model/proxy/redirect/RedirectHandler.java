package cn.edu.sztui.base.domain.model.proxy.redirect;

import cn.edu.sztui.base.domain.model.proxy.client.HttpResult;
import java.util.Optional;

/**
 * 重定向处理策略接口
 */
public interface RedirectHandler {
    /**
     * 尝试从响应中提取重定向URL
     * @param result HTTP响应结果
     * @param currentUrl 当前请求URL
     * @return 重定向URL，如果没有重定向则返回empty
     */
    Optional<String> extractRedirectUrl(HttpResult result, String currentUrl);
}
