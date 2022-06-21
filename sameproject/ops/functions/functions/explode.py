import dill


class BaseExplodingVariable:
    """Base class for ExplodingVariable."""

    def __is_exploding_variable__(self):
        """Allows detecting exploding variables without triggering them."""
        return True

    def __setattr__(self, *args):
        raise self.err

    def __getattr__(self, attr):
        raise self.err

    def __delattr__(self, *args):
        raise self.err

    def __repr__(self, *args):
        raise self.err

    def __str__(self, *args):
        raise self.err

    def __unicode__(self, *args):
        raise self.err

    def __bytes__(self, *args):
        raise self.err

    def __format__(self, *args):
        raise self.err

    def __lt__(self, *args):
        raise self.err

    def __le__(self, *args):
        raise self.err

    def __eq__(self, *args):
        raise self.err

    def __ne__(self, *args):
        raise self.err

    def __gt__(self, *args):
        raise self.err

    def __ge__(self, *args):
        raise self.err

    def __hash__(self, *args):
        raise self.err

    def __bool__(self, *args):
        raise self.err

    def __dir__(self, *args):
        raise self.err

    def __get__(self, *args):
        raise self.err

    def __set__(self, *args):
        raise self.err

    def __delete__(self, *args):
        raise self.err

    def __set_name__(self, *args):
        raise self.err

    def __instancecheck__(self, *args):
        raise self.err

    def __subclasscheck__(self, *args):
        raise self.err

    def __call__(self, *args):
        raise self.err

    def __len__(self, *args):
        raise self.err

    def __length_hint__(self, *args):
        raise self.err

    def __getitem__(self, *args):
        raise self.err

    def __setitem__(self, *args):
        raise self.err

    def __delitem__(self, *args):
        raise self.err

    def __missing__(self, *args):
        raise self.err

    def __item__(self, *args):
        raise self.err

    def __reversed__(self, *args):
        raise self.err

    def __contains__(self, *args):
        raise self.err

    def __add__(self, *args):
        raise self.err

    def __sub__(self, *args):
        raise self.err

    def __mul__(self, *args):
        raise self.err

    def __matmul__(self, *args):
        raise self.err

    def __truediv__(self, *args):
        raise self.err

    def __floordiv__(self, *args):
        raise self.err

    def __mod__(self, *args):
        raise self.err

    def __divmod__(self, *args):
        raise self.err

    def __pow__(self, *args):
        raise self.err

    def __lshift__(self, *args):
        raise self.err

    def __rshift__(self, *args):
        raise self.err

    def __and__(self, *args):
        raise self.err

    def __xor__(self, *args):
        raise self.err

    def __or__(self, *args):
        raise self.err

    def __radd__(self, *args):
        raise self.err

    def __rsub__(self, *args):
        raise self.err

    def __rmul__(self, *args):
        raise self.err

    def __rmatmul__(self, *args):
        raise self.err

    def __rtruediv__(self, *args):
        raise self.err

    def __rfloordiv__(self, *args):
        raise self.err

    def __rmod__(self, *args):
        raise self.err

    def __rdivmod__(self, *args):
        raise self.err

    def __rpow__(self, *args):
        raise self.err

    def __rlshift__(self, *args):
        raise self.err

    def __rrshift__(self, *args):
        raise self.err

    def __rand__(self, *args):
        raise self.err

    def __rxor__(self, *args):
        raise self.err

    def __ror__(self, *args):
        raise self.err

    def __iadd__(self, *args):
        raise self.err

    def __isub__(self, *args):
        raise self.err

    def __imul__(self, *args):
        raise self.err

    def __imatmul__(self, *args):
        raise self.err

    def __itruediv__(self, *args):
        raise self.err

    def __ifloordiv__(self, *args):
        raise self.err

    def __imod__(self, *args):
        raise self.err

    def __ipow__(self, *args):
        raise self.err

    def __ilshift__(self, *args):
        raise self.err

    def __irshift__(self, *args):
        raise self.err

    def __iand__(self, *args):
        raise self.err

    def __ixor__(self, *args):
        raise self.err

    def __ior__(self, *args):
        raise self.err

    def __neg__(self, *args):
        raise self.err

    def __pos__(self, *args):
        raise self.err

    def __abs__(self, *args):
        raise self.err

    def __invert__(self, *args):
        raise self.err

    def __complex__(self, *args):
        raise self.err

    def __int__(self, *args):
        raise self.err

    def __float__(self, *args):
        raise self.err

    def __index__(self, *args):
        raise self.err

    def __round__(self, *args):
        raise self.err

    def __trunc__(self, *args):
        raise self.err

    def __floor__(self, *args):
        raise self.err

    def __ceil__(self, *args):
        raise self.err

    def __enter__(self, *args):
        raise self.err

    def __exit__(self, *args):
        raise self.err


class ExplodingVariable(BaseExplodingVariable):
    """
    Exploding variables raise an error when anything is done with them. They
    are used to patch variables that cannot be serialised for various reasons
    when passing context between containers for different SAME steps. The
    error should inform the user of the reason the variable cannot be
    serialised - dill might not support it, it may use too much memory etc.

    Our approach is to patch all special methods on the class:
    https://docs.python.org/3/reference/datamodel.html#special-method-names
    """

    def __init__(self, err):
        self.err = err
        self.mro = "ExplodingVariable"

    # Patch to allow setting 'self.err' and 'self.mro' in the constructor.
    def __setattr__(self, attr, value):
        if attr in ["err", "mro"]:
            self.__dict__[attr] = value
            return

        super().__setattr__(self, attr, value)


# Custom deserialiser for ExplodingVariable that bypasses the explosion.
def deserialise(err):
    return ExplodingVariable(err)


# Custom serialiser for ExplodingVariable that bypasses the explosion.
@dill.register(ExplodingVariable)
def serialise(pickler, obj):
    pickler.save_reduce(deserialise, (obj.err,), obj=obj)
