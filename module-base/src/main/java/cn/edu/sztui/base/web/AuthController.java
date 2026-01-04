package cn.edu.sztui.base.web;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.LoginType;
import jakarta.annotation.Resource;
import org.springframework.http.ResponseEntity;
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
    public ResponseEntity<LoginType> loginType() {
        LoginType result = authService.loginCheck();
        return ResponseEntity.ok(result);
    }

    /**
     * 网关登录
     * @param request
     * @return
     */
    @PostMapping("/login")
    public ResponseEntity<LoginResultsVo> loginUsrPasswd(@RequestBody LoginRequestCommand request) {
        LoginResultsVo result = authService.loginFrame(request);
        return ResponseEntity.ok(result);
    }

    /**
     * 验证码过期，再次请求
     * @return
     */
    @GetMapping("/sms")
    public ResponseEntity<LoginResultsVo> getSms(@RequestParam("id") String id) {
        LoginResultsVo result = authService.getSms(id);
        return ResponseEntity.ok(result);
    }

//    @GetMapping("/crousetable")
//    public ResponseEntity<String> getCrousetable(@RequestBody CrouseTableQuery request) {
//        return null;
//    }

    // @PostMapping("/logout")
    // public ResponseEntity<String> logout(@RequestBody LoginRequestCommand request) {
    //     String result = vpnService.login();
    //     return ResponseEntity.ok(vpnService.logout);
    // }
}
