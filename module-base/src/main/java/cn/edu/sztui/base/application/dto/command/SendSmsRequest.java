package cn.edu.sztui.base.application.dto.command;

import lombok.Data;

@Data
public class SendSmsRequest {
    private String machineId;
    private String userId;
}
