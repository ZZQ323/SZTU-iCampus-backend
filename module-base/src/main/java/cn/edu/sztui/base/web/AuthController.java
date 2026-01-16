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

    @GetMapping("/v1/status/session")
    public Result getSessionStatus(@RequestParam String code) {
        return Result.ok("ok");
    }

    @PostMapping("/cookie/refresh")
    public Result refresh(@RequestBody String code){
        return Result.ok(authService.init());
    }

    /**
     * 网关登录
     * @param request
     * @return
     */
    @PostMapping("/v1/login")
    public Result loginUsrPasswd(@RequestBody LoginRequestCommand request) {
        LoginResultsVo result = authService.loginFrame(request);
        return Result.ok(result);
    }

    /**
     * 验证码过期，再次请求
     * @return
     */
    @PostMapping("/v1/request/sms")
    public Result getSms(@RequestParam("id") String id) {
        LoginResultsVo result = authService.getSms(id);
        return Result.ok(result);
    }

    @PostMapping("/v1/verify/sms")
    public Result verify(){
        return Result.ok("ok");
    }

     @PostMapping("/v1/logout")
     public Result logout(@RequestBody LoginRequestCommand request) {
         return Result.ok(authService.logout());
     }
}
