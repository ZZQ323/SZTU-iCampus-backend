package cn.edu.sztui.common.util.auth;

import lombok.Data;
import java.io.Serializable;

@Data
public class UserRole implements Serializable {
    private Integer userId;
    private Integer roleId;
}
