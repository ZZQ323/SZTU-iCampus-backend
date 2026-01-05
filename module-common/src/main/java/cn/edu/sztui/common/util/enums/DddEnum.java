package cn.edu.sztui.common.util.enums;

public enum DddEnum {
    WEB(1),
    APPLICATIN(2),
    DOMAIN(3),
    INFRASTRUCTURE(4);

    private Integer level;

    private DddEnum(Integer level) {
        this.level = level;
    }

    public Integer getLevel() {
        return this.level;
    }
}
