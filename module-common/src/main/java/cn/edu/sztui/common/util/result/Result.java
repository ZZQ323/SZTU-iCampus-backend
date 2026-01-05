package cn.edu.sztui.common.util.result;

import cn.edu.sztui.common.util.constant.CommonBizConstant;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import com.alibaba.fastjson2.JSONObject;

import java.util.HashMap;

public class Result extends HashMap<String, Object> {
    private static final long serialVersionUID = 1L;

    private Result() {
        this.put("actionType", CommonBizConstant.ZERO);
    }

    public static Result error() {
        return error(ResultCodeEnum.INTERNAL_SERVER_ERROR.httpStatus, "未知异常，请联系管理员");
    }

    public static Result error(String msg) {
        return error(ResultCodeEnum.INTERNAL_SERVER_ERROR.httpStatus, msg);
    }

    public static Result error(int code, String msg) {
        Result r = new Result();
        r.put("data", new JSONObject());
        r.put("code", code);
        r.put("message", msg);
        return r;
    }

    public static Result error(int code, String msg, int actionType) {
        Result r = new Result();
        r.put("data", new JSONObject());
        r.put("code", code);
        r.put("message", msg);
        r.put("actionType", actionType);
        return r;
    }

    public static Result ok(String msg) {
        Result r = new Result();
        r.put("code", ResultCodeEnum.SUCCESS.httpStatus);
        r.put("message", msg);
        r.put("data", new JSONObject());
        return r;
    }

    public static Result ok(Object object) {
        Result r = new Result();
        r.put("code", ResultCodeEnum.SUCCESS.httpStatus);
        r.put("message", "操作成功");
        r.put("data", object);
        return r;
    }

    public static Result ok() {
        Result r = new Result();
        r.put("code", ResultCodeEnum.SUCCESS.httpStatus);
        r.put("message", "操作成功");
        r.put("data", new JSONObject());
        return r;
    }

    public static Result save() {
        return code201(true);
    }

    public static Result save(boolean flag) {
        return code201(flag);
    }

    public static Result save(Object object) {
        return code201(object);
    }

    private static Result code201(boolean flag) {
        Result r = new Result();
        if (!flag) {
            r.put("code", SysReturnCode.OPERATION_UNSUCCESSFUL.code());
            r.put("message", SysReturnCode.OPERATION_UNSUCCESSFUL.message());
        } else {
            r.put("code", ResultCodeEnum.CREATED.httpStatus);
            r.put("message", "操作成功");
        }

        JSONObject object = new JSONObject();
        object.put("flag", flag);
        r.put("data", object);
        return r;
    }

    private static Result code201(Object object) {
        Result r = new Result();
        r.put("code", ResultCodeEnum.CREATED.httpStatus);
        r.put("message", "success");
        r.put("data", object);
        return r;
    }

    public static Result delete() {
        Result r = new Result();
        r.put("code", ResultCodeEnum.NO_CONTENT.httpStatus);
        r.put("message", "操作成功");
        r.put("data", new JSONObject());
        return r;
    }

    public static Result delete(boolean flag) {
        Result r = new Result();
        if (!flag) {
            r.put("code", SysReturnCode.OPERATION_UNSUCCESSFUL.code());
            r.put("message", SysReturnCode.OPERATION_UNSUCCESSFUL.message());
        } else {
            r.put("code", ResultCodeEnum.NO_CONTENT.httpStatus);
            r.put("message", "操作成功");
        }

        JSONObject object = new JSONObject();
        object.put("flag", flag);
        r.put("data", object);
        return r;
    }

    public static Result delete(Object object) {
        Result r = new Result();
        r.put("code", ResultCodeEnum.NO_CONTENT.httpStatus);
        r.put("message", "操作成功");
        r.put("data", object);
        return r;
    }

    public static Result update() {
        return code201(true);
    }

    public static Result update(boolean flag) {
        return code201(flag);
    }

    public static Result update(Object object) {
        return code201(object);
    }
}
