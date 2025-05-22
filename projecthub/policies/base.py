from rest_framework.exceptions import PermissionDenied


class OperationHolderMixin:
    def __and__(self, other):
        return OperandHolder(AND, self, other)

    def __or__(self, other):
        return OperandHolder(OR, self, other)

    def __rand__(self, other):
        return OperandHolder(AND, other, self)

    def __ror__(self, other):
        return OperandHolder(OR, other, self)

    def __invert__(self):
        return SingleOperandHolder(NOT, self)


class SingleOperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class):
        self.operator_class = operator_class
        self.op1_class = op1_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        return self.operator_class(op1)


class OperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class, op2_class):
        self.operator_class = operator_class
        self.op1_class = op1_class
        self.op2_class = op2_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        op2 = self.op2_class(*args, **kwargs)
        return self.operator_class(op1, op2)

    def __eq__(self, other):
        return (
                isinstance(other, OperandHolder) and
                self.operator_class == other.operator_class and
                self.op1_class == other.op1_class and
                self.op2_class == other.op2_class
        )

    def __hash__(self):
        return hash((self.operator_class, self.op1_class, self.op2_class))


class AND:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_access(self, request, view):
        return (
                self.op1.has_access(request, view) and
                self.op2.has_access(request, view)
        )

    def has_object_access(self, request, view, obj):
        return (
                self.op1.has_object_access(request, view, obj) and
                self.op2.has_object_access(request, view, obj)
        )


class OR:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_access(self, request, view):
        return (
                self.op1.has_access(request, view) or
                self.op2.has_access(request, view)
        )

    def has_object_access(self, request, view, obj):
        return (
                self.op1.has_access(request, view)
                and self.op1.has_object_access(request, view, obj)
        ) or (
                self.op2.has_access(request, view)
                and self.op2.has_object_access(request, view, obj)
        )


class NOT:
    def __init__(self, op1):
        self.op1 = op1

    def has_access(self, request, view):
        return not self.op1.has_access(request, view)

    def has_object_access(self, request, view, obj):
        return not self.op1.has_object_access(request, view, obj)


class BasePolicyMetaclass(OperationHolderMixin, type):
    pass


class BasePolicy(metaclass=BasePolicyMetaclass):
    """
    A base class from which all policies classes should inherit.
    """

    def has_access(self, request, view):
        return True

    def has_object_access(self, request, view, obj):
        return True


class AllowAnyPolicy(BasePolicy):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    policy_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_access(self, request, view):
        return True


class IsAuthenticatedPolicy(BasePolicy):
    """
    Allows access only to authenticated users.
    """

    def has_access(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        return True


class IsAdminUserPolicy(BasePolicy):
    """
    Allows access only to admin users.
    """

    def has_access(self, request, view):
        return bool(request.user and request.user.is_staff)
