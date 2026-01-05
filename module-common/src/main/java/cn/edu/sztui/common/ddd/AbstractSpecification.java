package cn.edu.sztui.common.ddd;

public abstract class AbstractSpecification<T> implements Specification<T> {
    public abstract boolean isSatisfiedBy(T var1);

    public Specification<T> and(Specification<T> specification) {
        return new AndSpecification(this, specification);
    }

    public Specification<T> or(Specification<T> specification) {
        return new OrSpecification(this, specification);
    }

    public Specification<T> not(Specification<T> specification) {
        return new NotSpecification(specification);
    }
}
