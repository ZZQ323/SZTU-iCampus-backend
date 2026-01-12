package cn.edu.sztui.base.application.dto.command;

import lombok.Data;

@Data
public class InitialRequest {
    private String code;
    private String deviceToken;
}
