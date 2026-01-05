package cn.edu.sztui.common.util.exception;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class BusinessException extends RuntimeException {
    private Integer code;
    private String message;
    private Integer actionType;
}
