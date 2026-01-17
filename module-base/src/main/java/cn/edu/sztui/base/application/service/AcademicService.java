package cn.edu.sztui.base.application.service;

import cn.edu.sztui.base.application.vo.LoginResultsVo;

public interface AcademicService {
    LoginResultsVo init(String tempCode);
    String getCrouseTable();
}
