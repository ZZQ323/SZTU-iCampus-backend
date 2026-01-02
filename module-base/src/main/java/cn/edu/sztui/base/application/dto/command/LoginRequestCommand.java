package cn.edu.sztui.base.application.dto.command;

import lombok.Data;

@Data
public class LoginRequestCommand {
    private String userId;
    private String password;
}
