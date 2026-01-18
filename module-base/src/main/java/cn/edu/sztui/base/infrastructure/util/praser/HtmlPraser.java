package cn.edu.sztui.base.infrastructure.util.praser;

import cn.edu.sztui.base.application.vo.LoginResultsVo;


public class HtmlPraser {
    /**
     * 使用正则表达式作为备选方案
     */
    public static void extractByRegex(LoginResultsVo ret,String htmlContent) {
        // 提取姓名
        java.util.regex.Pattern namePattern = java.util.regex.Pattern.compile("姓名[：:]([^<>\n]+)");
        java.util.regex.Matcher nameMatcher = namePattern.matcher(htmlContent);
        if (nameMatcher.find()) {
            String userName = nameMatcher.group(1).trim();
            ret.setRealName(userName);
        }

        // 提取工号
        java.util.regex.Pattern idPattern = java.util.regex.Pattern.compile("工号[：:]([^<>\n]+)");
        java.util.regex.Matcher idMatcher = idPattern.matcher(htmlContent);
        if (idMatcher.find()) {
            String userId = idMatcher.group(1).trim();
            ret.setUserId(userId);
        }

        // 提取部门
        java.util.regex.Pattern deptPattern = java.util.regex.Pattern.compile("部门[：:]([^<>\n]+)");
        java.util.regex.Matcher deptMatcher = deptPattern.matcher(htmlContent);
        if (deptMatcher.find()) {
            String department = deptMatcher.group(1).trim();
            ret.setSchoolName(department);
        }

        // 提取性别
        java.util.regex.Pattern genderPattern = java.util.regex.Pattern.compile("性别[：:]([^<>\n]+)");
        java.util.regex.Matcher genderMatcher = genderPattern.matcher(htmlContent);
        if (genderMatcher.find()) {
            String gender = genderMatcher.group(1).trim();
            ret.setGender(gender);
        }
    }
}
