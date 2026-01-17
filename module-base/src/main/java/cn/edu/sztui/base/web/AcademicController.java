package cn.edu.sztui.base.web;

import cn.edu.sztui.base.application.service.AcademicService;
import cn.edu.sztui.common.util.result.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/acdmadminsys")
public class AcademicController {

    @Autowired
    private AcademicService academicService;

    /**
     * 检验token是否过期
     */
    @GetMapping("/active")
    public Result isActive() {
        return Result.ok("success");
    }

    /**
     * 获取课表
     * @param
     * @return
     */
    @GetMapping("/schedule")
    public Result getCrousetable() {
        return Result.ok(academicService.getCrouseTable());
    }
}
