package cn.edu.sztui.base.web;

import cn.edu.sztui.base.application.dto.command.*;
import cn.edu.sztui.base.application.service.ProxyService;
import cn.edu.sztui.base.application.vo.ProxyInitVO;
import cn.edu.sztui.base.application.vo.ProxyLoginResultVO;
import cn.edu.sztui.common.util.result.Result;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

/**
 * 代理服务控制器
 */
@RestController
@Slf4j
@RequestMapping("/proxy")
public class ProxyController {

    @Resource
    private ProxyService proxyService;

    /**
     * 初始化会话（获取机器Cookie）
     * 调用流程：前端首次访问时调用，获取machineId
     */
    @PostMapping("/init")
    public Result initSession(@RequestBody InitialRequest initialRequest) {
        ProxyInitVO vo = proxyService.initSession(initialRequest.getCode(),initialRequest.getDeviceToken());
        return Result.ok(vo);
    }

    /**
     * 2. 发送短信验证码
     */
    @PostMapping("/send-sms")
    public Result sendSms(@RequestBody SendSmsRequest request) {
        boolean success = proxyService.sendSms(request.getMachineId(), request.getUserId());
        return Result.ok(success);
    }

    /**
     * 3. 登录
     */
    @PostMapping("/sms-login")
    public Result login(@RequestBody ProxyLoginCommand command) {
        ProxyLoginResultVO vo = proxyService.login(command);
        return Result.ok(vo);
    }

    /**
     * 4. 代理访问学校API
     */
    @GetMapping("/api")
    public Result proxyApi(
            @RequestParam String machineId,
            @RequestParam String apiUrl) {
        String response = proxyService.proxyApi(machineId, apiUrl);
        return Result.ok(response);
    }

    /**
     * POST方式代理API（用于需要传参的接口）
     */
    @PostMapping("/api")
    public Result proxyApiPost(@RequestBody ProxyApiRequest request) {
        String response = proxyService.proxyApi(request.getMachineId(), request.getApiUrl());
        return Result.ok(response);
    }

    /**
     * 5. 检查会话状态
     */
    @GetMapping("/check")
    public Result checkSession(@RequestParam String machineId) {
        boolean valid = proxyService.checkSession(machineId);
        return Result.ok(valid);
    }

    /**
     * 6. 登出
     */
    @PostMapping("/logout")
    public Result logout(@RequestBody LogoutRequest request) {
        proxyService.logout(request.getMachineId());
        return Result.ok();
    }
}
