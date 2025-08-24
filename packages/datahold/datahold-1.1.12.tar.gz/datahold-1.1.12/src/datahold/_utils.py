import abc
import inspect as ins
from types import FunctionType
from typing import *

__all__ = [
    "holdDecorator",
]

INITDOC: str = "This property represents the underlying data of the current instance."


class holdDecorator:
    _funcnames: tuple[str]

    def __call__(self: Self, holdcls: type) -> type:
        self.setupDataProperty(holdcls=holdcls)
        self.setupInitFunc(holdcls=holdcls)
        name: str
        for name in self._funcnames:
            self.setupHoldFunc(holdcls=holdcls, name=name)
        abc.update_abstractmethods(holdcls)
        return holdcls

    def __init__(self: Self, *funcnames: str) -> None:
        self._funcnames = funcnames

    @classmethod
    def makeDataProperty(cls: type, *, datacls: type) -> property:
        def fget(self: Self) -> Any:
            return datacls(self._data)

        def fset(self: Self, value: Any) -> None:
            self._data = datacls(value)

        ans: property = property(fget=fget, fset=fset, doc=INITDOC)
        return ans

    @classmethod
    def makeHoldFunc(cls: type, *, old: FunctionType) -> Any:
        def new(self: Self, *args: Any, **kwargs: Any) -> Any:
            data: Any = self.data
            ans: Any = old(data, *args, **kwargs)
            self.data = data
            return ans

        new.__doc__ = old.__doc__

        return new

    @classmethod
    def makeInitFunc(cls: type, *, datacls: type) -> FunctionType:
        def new(self: Self, *args: Any, **kwargs: Any) -> Any:
            self.data = datacls(*args, **kwargs)

        new.__doc__ = datacls.__init__.__doc__

        return new

    @classmethod
    def setupDataProperty(cls: type, holdcls: type) -> None:
        datacls: type = holdcls.__annotations__["data"]
        holdcls.data = cls.makeDataProperty(datacls=datacls)

    @classmethod
    def setupHoldFunc(cls: type, holdcls: type, *, name: str) -> None:
        datacls: type = holdcls.__annotations__["data"]
        old: Callable = getattr(datacls, name)
        new: FunctionType = cls.makeHoldFunc(old=old)
        new.__module__ = holdcls.__module__
        new.__name__ = name
        new.__qualname__ = holdcls.__qualname__ + "." + name
        cls.updateSignature(old=old, new=new)
        setattr(holdcls, name, new)

    @classmethod
    def setupInitFunc(cls: type, holdcls: type) -> None:
        datacls: type = holdcls.__annotations__["data"]
        new = cls.makeInitFunc(datacls=datacls)
        old = datacls.__init__
        new.__module__ = holdcls.__module__
        new.__name__ = "__init__"
        new.__qualname__ = holdcls.__qualname__ + ".__init__"
        cls.updateSignature(old=old, new=new)
        holdcls.__init__ = new

    @classmethod
    def updateSignature(
        cls: type,
        *,
        old: Callable,
        new: FunctionType,
    ) -> ins.Signature:
        try:
            oldsig: ins.Signature = ins.signature(old)
        except ValueError:
            return
        params: list = list()
        a: Any
        n: int
        p: ins.Parameter
        q: ins.Parameter
        for n, p in enumerate(oldsig.parameters.values()):
            if n == 0:
                a = Self
            elif p.annotation is ins.Parameter.empty:
                a = Any
            else:
                a = p.annotation
            q = p.replace(annotation=a)
            params.append(q)
        if oldsig.return_annotation is ins.Parameter.empty:
            a = Any
        else:
            a = oldsig.return_annotation
        new.__signature__ = ins.Signature(params, return_annotation=a)
