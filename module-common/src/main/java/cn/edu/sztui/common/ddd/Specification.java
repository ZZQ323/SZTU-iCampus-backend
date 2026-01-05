package cn.edu.sztui.common.ddd;

public interface Specification<T> {
    boolean isSatisfiedBy(T var1);

    Specification<T> and(Specification<T> var1);

    Specification<T> or(Specification<T> var1);

    Specification<T> not(Specification<T> var1);
}

