from __future__ import annotations

import abc
import functools
import types
from typing import *

from datarepr import datarepr
from frozendict import frozendict
from makeprop import makeprop
from unhash import unhash

__all__ = ["BaseArgumentHolder", "ArgumentHolder", "FrozenArgumentHolder"]


class BaseArgumentHolder(abc.ABC):

    __slots__ = ("_args", "_kwargs")

    @abc.abstractmethod
    def __eq__(self: Self, other: Any, /) -> bool: ...

    @abc.abstractmethod
    def __hash__(self: Self) -> int: ...

    @abc.abstractmethod
    def __init__(self: Self, *args: Any, **kwargs: Any) -> None: ...

    def __len__(self: Self) -> int:
        "This magic method implements len(self)."
        return len(self.args) + len(self.kwargs)

    def __matmul__(self: Self, other: Callable) -> Self:
        "This magic method implements self@other."
        x: Any
        y: Any
        args: list = [other(x) for x in self.args]
        kwargs: dict = {x: other(y) for x, y in self.kwargs.items()}
        ans: Self = type(self)(*args, **kwargs)
        return ans

    def __repr__(self: Self) -> str:
        "This magic method implements repr(self)."
        return datarepr(type(self).__name__, *self.args, **self.kwargs)

    def __rmatmul__(self: Self, other: Callable) -> Self:
        "This magic method implements other@self."
        return self @ other

    @property
    @abc.abstractmethod
    def args(self): ...

    def call(self: Self, callback: Callable, /) -> Any:
        "This method calls a callback using the arguments in the current instance."
        return callback(*self.args, **self.kwargs)

    def copy(self: Self) -> Self:
        "This method makes a copy of the current instance."
        return self.call(type(self))

    @property
    @abc.abstractmethod
    def kwargs(self: Self): ...

    def partial(self: Self, func: Callable, /) -> functools.partial:
        "This method creates a functools.partial object."
        return functools.partial(func, *self.args, **self.kwargs)

    def partialmethod(self: Self, func: Callable, /) -> functools.partialmethod:
        "This method creates a functools.partialmethod object."
        return functools.partialmethod(
            func,
            *self.args,
            **self.kwargs,
        )

    def toArgumentHolder(self: Self) -> ArgumentHolder:
        "This method converts the current instance into an ArgumentHolder object."
        return self.call(ArgumentHolder)

    def toFrozenArgumentHolder(self: Self) -> FrozenArgumentHolder:
        "This method converts the current instance into a FrozenArgumentHolder object."
        return self.call(FrozenArgumentHolder)


class ArgumentHolder(BaseArgumentHolder):

    def __eq__(self: Self, other: Any, /) -> bool:
        "This magic method implements self==other."
        if not isinstance(other, ArgumentHolder):
            return False
        return (self.args, self.kwargs) == (other.args, other.kwargs)

    __hash__ = unhash

    def __init__(self: Self, *args: Any, **kwargs: Any) -> None:
        "This magic method sets up the current instance."
        self._args = list(args)
        self._kwargs = dict(kwargs)

    def __imatmul__(self: Self, other: Callable) -> Self:
        "This magic method implements self@=other."
        x: Any
        y: Any
        args0: list = list(self.args)
        kwargs0: dict = dict(self.kwargs)
        args: list = [other(x) for x in self.args]
        kwargs: dict = {x: other(y) for x, y in self.kwargs.items()}
        try:
            self.args = args
            self.kwargs = kwargs
        except BaseException as exc:
            self.args = args0
            self.kwargs = kwargs0
            raise
        else:
            return self

    @makeprop(delete=())
    def args(self: Self, value: Iterable) -> None:
        "This property holds the positional arguments."
        value: list = list(value)
        self._args.clear()
        self._args.extend(value)
        return self._args

    @makeprop(delete=())
    def kwargs(self: Self, value: Any) -> None:
        "This property holds the keyword arguments."
        value: dict = dict(value)
        self._kwargs.clear()
        self._kwargs.update(value)
        return self._kwargs


class FrozenArgumentHolder(BaseArgumentHolder):

    def __eq__(self: Self, other: Any, /) -> bool:
        "This magic method implements self==other."
        if not isinstance(other, FrozenArgumentHolder):
            return False
        return (self.args, self.kwargs) == (other.args, other.kwargs)

    def __hash__(self: Self) -> int:
        "This magic method implements hash(self)."
        return (self.args, self.kwargs).__hash__()

    def __init__(self: Self, *args: Any, **kwargs: Any) -> None:
        "This magic method sets up the current instance."
        self._args = tuple(args)
        self._kwargs = frozendict(kwargs)

    @property
    def args(self: Self) -> tuple:
        "This property holds the positional arguments."
        return self._args

    @property
    def kwargs(self: Self) -> frozendict:
        "This property holds the keyword arguments."
        return self._kwargs
