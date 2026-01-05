package cn.edu.sztui.common.ddd;

public class AndSpecification<T> extends AbstractSpecification<T> {
    private Specification<T> spec1;
    private Specification<T> spec2;

    public AndSpecification(Specification<T> spec1, Specification<T> spec2) {
        this.spec1 = spec1;
        this.spec2 = spec2;
    }

    public boolean isSatisfiedBy(T t) {
        return this.spec1.isSatisfiedBy(t) && this.spec2.isSatisfiedBy(t);
    }
}
