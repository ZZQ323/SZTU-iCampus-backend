package cn.edu.sztui.common.util.jwt;

import cn.edu.sztui.common.util.enums.SysChannelEnum;
import jakarta.servlet.http.HttpServletRequest;

public interface  SysChannelConstant {
    String INDEX_OF = "|";
    String STR_NULL = "null";
    String HEAD_WS_CLIENT = "ws-client";
    String HEAD_TOKEN = "token";
    String WS_CLIENT_WEB = "web";
    String WS_CLIENT_APP = "app";
    String WS_CLIENT_BPAPP = "bpapp";
    String WS_CLIENT_VM = "vm";
    String WS_CLIENT_WXMINI = "wxmini";

    static SysChannelEnum checkChannel(HttpServletRequest request) {
        String client = request.getHeader("token");
        if (client != null && !"".equals(client) && !"null".equals(client)) {
            if (client.indexOf("|") == -1) {
                client = request.getHeader("ws-client");
                if (client == null || "".equals(client) || "null".equals(client)) {
                    return null;
                }
            } else {
                client = client.substring(0, client.indexOf("|")).toLowerCase();
            }
        } else {
            client = request.getHeader("ws-client");
        }

        SysChannelEnum channel = null;
        if ("web".equals(client)) {
            channel = SysChannelEnum.WEB;
        } else if ("app".equals(client)) {
            channel = SysChannelEnum.APP;
        } else if ("bpapp".equals(client)) {
            channel = SysChannelEnum.BPAPP;
        } else if ("vm".equals(client)) {
            channel = SysChannelEnum.VM;
        } else if ("wxmini".equals(client)) {
            channel = SysChannelEnum.WXMINI;
        }

        return channel;
    }
}
