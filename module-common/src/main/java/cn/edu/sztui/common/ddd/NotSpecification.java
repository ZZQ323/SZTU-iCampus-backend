package cn.edu.sztui.common.ddd;

public class NotSpecification<T> extends AbstractSpecification<T> {
    private Specification<T> spec1;

    public NotSpecification(Specification<T> spec1) {
        this.spec1 = spec1;
    }

    public boolean isSatisfiedBy(T t) {
        return !this.spec1.isSatisfiedBy(t);
    }
}

