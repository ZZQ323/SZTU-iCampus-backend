package cn.edu.sztui.base.web;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.dto.query.CrouseTableQuery;
import cn.edu.sztui.base.application.service.LoginService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import jakarta.annotation.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/usr")
public class AcademicSysController {

    @Resource
    private LoginService loginService;

    /**
     * 网关登录
     * @param request
     * @return
     */
    @PostMapping("/login")
    public ResponseEntity<LoginResultsVo> login(@RequestBody LoginRequestCommand request) {
        LoginResultsVo result = loginService.loginWithPasswd(request.getUserId(), request.getPassword());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/crousetable")
    public ResponseEntity<String> getCrousetable(@RequestBody CrouseTableQuery request) {
        return null;
    }

    // @PostMapping("/logout")
    // public ResponseEntity<String> logout(@RequestBody LoginRequestCommand request) {
    //     String result = vpnService.login();
    //     return ResponseEntity.ok(vpnService.logout);
    // }
}
