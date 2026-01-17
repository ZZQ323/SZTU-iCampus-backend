package cn.edu.sztui.common.util.enums;

public enum SysChannelEnum  {
    APP(1),
    BPAPP(2),
    WEB(3),
    VM(4),
    WXMINI(5);

    private Integer channel;

    private SysChannelEnum(Integer channel) {
        this.channel = channel;
    }

    public static SysChannelEnum getByChannel(Integer channel) {
        for(SysChannelEnum sysChannelEnum : values()) {
            if (sysChannelEnum.getChannel().equals(channel)) {
                return sysChannelEnum;
            }
        }

        return null;
    }

    public static SysChannelEnum matchChannel(String channelName) {
        for(SysChannelEnum sysChannel : values()) {
            if (sysChannel.name().equalsIgnoreCase(channelName)) {
                return sysChannel;
            }
        }

        return null;
    }

    public Integer getChannel() {
        return this.channel;
    }
}
