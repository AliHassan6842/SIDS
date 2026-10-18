package com.agrosense.audit.infrastructure;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface Auditable {

    /**
     * The action identifier (e.g. "FARM_CREATED", "DIAGNOSIS_SUBMITTED").
     */
    String action();

    /**
     * The entity type affected (e.g. "FARM", "DIAGNOSIS", "FIELD").
     */
    String entityType() default "";
}
