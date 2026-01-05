package cn.edu.sztui.base.web;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import cn.edu.sztui.common.util.result.Result;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/usr")
public class AuthController {

    @Resource
    private AuthService authService;

    /**
     * 检查登录方式
     * @param
     * @return
     */
    @GetMapping("/login")
    public Result loginType() {
        LoginType result = authService.loginCheck();
        return Result.ok(result);
    }

    /**
     * 网关登录
     * @param request
     * @return
     */
    @PostMapping("/login")
    public Result loginUsrPasswd(@RequestBody LoginRequestCommand request) {
        LoginResultsVo result = authService.loginFrame(request);
        return Result.ok(result);
    }

    /**
     * 验证码过期，再次请求
     * @return
     */
    @GetMapping("/sms")
    public Result getSms(@RequestParam("id") String id) {
        LoginResultsVo result = authService.getSms(id);
        return Result.ok(result);
    }

     @PostMapping("/logout")
     public Result logout(@RequestBody LoginRequestCommand request) {
         return Result.ok(authService.logout());
     }
}
