package cn.edu.sztui.common.util.exception;

import cn.edu.sztui.common.util.enums.DddEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.hutool.core.util.ObjectUtil;
import lombok.Data;

@Data
public class BusinessException extends RuntimeException {
    private Integer code;
    private String message;
    private Integer actionType;

    public BusinessException(SysReturnCode returnCode, DddEnum dddEnum, String message) {
        String code = returnCode.code() + "" + dddEnum.getLevel();
        this.code = Integer.valueOf(code);
        this.message = ObjectUtil.isNotNull(message) ? message : returnCode.message();
    }

    public BusinessException(Integer code, String message) {
        super(message);
        this.message = message;
        this.code = code;
    }

    public BusinessException(Integer code, String message, Integer actionType) {
        super(message);
        this.message = message;
        this.code = code;
        this.actionType = actionType;
    }
}
