package cn.edu.sztui.base.application.dto.command;

import lombok.Data;

@Data
public class ProxyApiRequest {
    private String machineId;
    private String apiUrl;
}
