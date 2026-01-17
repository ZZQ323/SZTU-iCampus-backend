package cn.edu.sztui.common.util.auth;

import java.lang.annotation.*;

@Inherited
@Documented
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface NoCheckLoginAnnotation {
}
