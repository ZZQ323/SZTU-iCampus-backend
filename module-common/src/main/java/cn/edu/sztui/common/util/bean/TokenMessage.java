package cn.edu.sztui.common.util.bean;

import cn.edu.sztui.common.util.enums.SysChannelEnum;
import lombok.Data;
import java.io.Serializable;
import java.util.List;

@Data
public class TokenMessage implements Serializable {
    private static final long serialVersionUID = 1L;
    // private String openId;
    private String unionId;
    private String sessionKey;       // 可选，用于解密微信数据
    private Long loginTime;          // 登录时间
    private Long expireTime;         // 过期时间
    private List<Integer> roleIds;
    private SysChannelEnum sysChannel;
}
