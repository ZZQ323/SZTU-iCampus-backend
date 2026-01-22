package cn.edu.sztui.common.util.log;

import com.alibaba.fastjson2.JSONObject;

public class LogMark {
    public static String format(String mark, String content) {
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("mark", mark);
        jsonObject.put("content", content);
        return jsonObject.toJSONString();
    }

    public static String format(String mark) {
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("mark", mark);
        return jsonObject.toJSONString();
    }
}
