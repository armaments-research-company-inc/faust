"""Object utilities."""
from typing import Any, Callable, Iterable, Type, cast

__all__ = ['iter_mro_reversed', 'cached_property']


def iter_mro_reversed(cls: Type, stop: Type) -> Iterable[Type]:
    """Iterate over superclasses, in reverse Method Resolution Order.

    The stop argument specifies a base class that when seen will
    stop iterating (well actually start, since this is in reverse, see Example
    for demonstration).

    Arguments:
        cls (Type): Target class.
        stop (Type): A base class in which we stop iteration.

    Notes:
        The last item produced will be the class itself (`cls`).

    Examples:
        >>> class A: ...
        >>> class B(A): ...
        >>> class C(B): ...

        >>> list(iter_mro_reverse(C, object))
        [A, B, C]

        >>> list(iter_mro_reverse(C, A))
        [B, C]

    Yields:
        Iterable[Type]: every class.
    """
    wanted = False
    for subcls in reversed(cls.__mro__):
        if wanted:
            yield cast(Type, subcls)
        else:
            wanted = subcls == stop


class cached_property(object):
    """Cached property.

    A property descriptor that caches the return value
    of the get function.

    Examples:
        .. code-block:: python

            @cached_property
            def connection(self):
                return Connection()

            @connection.setter  # Prepares stored value
            def connection(self, value):
                if value is None:
                    raise TypeError('Connection must be a connection')
                return value

            @connection.deleter
            def connection(self, value):
                # Additional action to do at del(self.attr)
                if value is not None:
                    print('Connection {0!r} deleted'.format(value)
    """

    def __init__(self,
                 fget: Callable = None,
                 fset: Callable = None,
                 fdel: Callable = None,
                 doc: str = None,
                 class_attribute=None) -> None:
        self.__get = fget
        self.__set = fset
        self.__del = fdel
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        self.class_attribute = class_attribute

    def __get__(self, obj: Any, type: Type = None) -> Any:
        if obj is None:
            if type is not None and self.class_attribute:
                return getattr(type, self.class_attribute)
            return self
        try:
            return obj.__dict__[self.__name__]
        except KeyError:
            value = obj.__dict__[self.__name__] = self.__get(obj)
            return value

    def __set__(self, obj: Any, value: Any) -> None:
        if self.__set is not None:
            value = self.__set(obj, value)
        obj.__dict__[self.__name__] = value

    def __delete__(self, obj: Any, _sentinel: Any = object()) -> None:
        value = obj.__dict__.pop(self.__name__, _sentinel)
        if self.__del is not None and value is not _sentinel:
            self.__del(obj, value)

    def setter(self, fset: Callable) -> 'cached_property':
        return self.__class__(self.__get, fset, self.__del)

    def deleter(self, fdel: Callable) -> 'cached_property':
        return self.__class__(self.__get, self.__set, fdel)
