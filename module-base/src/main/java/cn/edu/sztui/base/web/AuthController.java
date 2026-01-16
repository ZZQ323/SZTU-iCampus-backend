package cn.edu.sztui.base.web;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.common.util.result.Result;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @Resource
    private AuthService authService;

    /**
     * 检测 unionID的 状态
     * @param tempCode
     * @return
     */
    @GetMapping("/v1/status/session")
    public Result getSessionStatus(@RequestParam String tempCode) {
        return Result.ok(authService.getSessionStatus(tempCode));
    }

    /**
     * 验证码过期，再次请求
     * @return
     */
    @PostMapping("/v1/request/sms")
    public Result getSms(@RequestBody LoginRequestCommand request) {
        LoginResultsVo result = authService.getSms(request.getWxCode(),request.getUserId());
        return Result.ok(result);
    }

    /**
     * 初始化新的cookie
     * @param request
     * @return
     */
    @PostMapping("/v1/cookie/refresh")
    public Result refresh(@RequestBody LoginRequestCommand request){
        return Result.ok(authService.init(request.getWxCode()));
    }

    /**
     * 网关账密登录
     * @param request
     * @return
     */
    @PostMapping("/v1/login/passwd")
    public Result loginUsrPasswd(@RequestBody LoginRequestCommand request) {
        LoginResultsVo result = authService.loginFrame(request);
        return Result.ok(result);
    }

    /**
     * 网关验证码登录
     * @param request
     * @return
     */
    @PostMapping("/v1/login/sms")
    public Result loginSms(@RequestBody LoginRequestCommand request) {
        return Result.ok(authService.loginFrame(request));
    }

     @PostMapping("/v1/logout")
     public Result logout(@RequestBody LoginRequestCommand request) {
         return Result.ok(authService.logout(request));
     }
}
