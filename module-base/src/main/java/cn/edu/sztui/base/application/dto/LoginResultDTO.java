package cn.edu.sztui.base.application.dto;

import lombok.Data;

@Data
public class LoginResultDTO {
    private Object cookies;
    private String html;
    private Object jsonResponses;
}
