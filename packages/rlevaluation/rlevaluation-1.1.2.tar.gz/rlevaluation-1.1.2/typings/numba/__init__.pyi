# from typing import Callable
from typing import Any, Callable, overload, TypeVar, Sequence

T = TypeVar('T')

@overload
def njit(cache: bool = False, parallel: bool = False, nogil: bool = False, fastmath: bool = False, inline: str = 'never') -> Callable[[T], T]: ...
@overload
def njit(f: T, cache: bool = False, parallel: bool = False, nogil: bool = False, fastmath: bool = False, inline: str = 'never') -> T: ...

def jit(cache: bool, forceobj: bool) -> Callable[[T], T]: ...

def vectorize(f: Any, cache: bool) -> Any: ...


def prange(end: int) -> Sequence[int]: ...

objmode: Any
