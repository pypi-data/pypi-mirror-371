# stack_lab/core.py
# -----------------------------------------------------------------------------
# MIT License
#
# A production-grade, feature-rich Stack for Python with:
# - O(1) push/pop/peek
# - Optional O(1) min()/max() via auxiliary stacks
# - Capacity control with overflow strategies
# - Bulk operations
# - Event hooks (on_change) with built-in 'print' observer
# - Transactions (begin/commit/rollback) + context-manager style
# - Snapshot/restore, cloning, functional transforms (map/filter)
# - Rotation, unique/dedup, count/find helpers
# - Typed, generic API with rich dunder methods for Pythonic use
#
# Designed by Anbu (stack-lab) — crafted to impress on PyPI ✨
# -----------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
)

T = TypeVar("T")

# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class StackError(Exception):
    """Base class for stack-lab exceptions."""


class StackEmptyError(StackError):
    """Raised when an operation requires elements but the stack is empty."""


class StackCapacityError(StackError):
    """Raised when capacity is exceeded and overflow strategy is 'error'."""


class StackTransactionError(StackError):
    """Raised when an invalid transaction operation occurs."""


# -----------------------------------------------------------------------------
# Config / Types
# -----------------------------------------------------------------------------
class OverflowStrategy(str, Enum):
    """How to behave when `maxsize` would be exceeded on push."""
    ERROR = "error"          # raise StackCapacityError
    DROP_OLDEST = "drop_oldest"  # drop from bottom to make room
    DROP_NEWEST = "drop_newest"  # refuse the incoming element (no-op)
    GROW = "grow"            # ignore maxsize (acts unbounded)


ChangeEvent = Literal["push", "pop", "clear"]


@dataclass(frozen=True)
class Snapshot(Generic[T]):
    """Immutable snapshot of the stack contents (top is last)."""
    items: Tuple[T, ...]
    track_minmax: bool


# -----------------------------------------------------------------------------
# Stack
# -----------------------------------------------------------------------------
class Stack(Generic[T]):
    """
    A modern, insanely capable LIFO stack.

    Features
    --------
    - O(1) push/pop/peek
    - Optional O(1) min()/max() tracking
    - Capacity control + overflow strategies
    - Bulk ops: push_many, pop_many
    - Transactions: begin/commit/rollback or `with s.transaction(): ...`
    - Event hooks: subscribe callbacks or use built-in 'print' observer
    - Functional helpers: map_new, filter_new
    - Utilities: rotate, unique (dedup), count, find
    - Snapshot/restore, clone, copy, to_list/from_iterable

    Examples
    --------
    >>> s = Stack[int](track_minmax=True, maxsize=3, overflow=OverflowStrategy.DROP_OLDEST)
    >>> s.push_many([3, 1, 4]); s.min(), s.max()
    (1, 4)
    >>> s.push(2)  # drops oldest (3) to respect capacity
    >>> s.to_list()
    [1, 4, 2]
    >>> with s.transaction() as tx:
    ...     tx.push(99)
    ...     raise RuntimeError("rollback me")
    Traceback (most recent call last):
        ...
    RuntimeError: rollback me
    >>> s.peek()
    2
    """

    # -------------------------- construction --------------------------
    def __init__(
        self,
        *items: T,
        track_minmax: bool = False,
        maxsize: Optional[int] = None,
        overflow: OverflowStrategy = OverflowStrategy.ERROR,
        on_change: Optional[Iterable[Callable[[ChangeEvent, "Stack[T]"], None]] | Iterable[str]] = None,
    ) -> None:
        """
        Parameters
        ----------
        items:
            Initial items to push (left→right = bottom→top).
        track_minmax:
            If True, min()/max() are O(1) using auxiliary stacks.
        maxsize:
            Optional capacity. If None, unbounded (unless overflow=GROW which
            also behaves unbounded).
        overflow:
            Strategy when capacity reached: 'error' | 'drop_oldest' |
            'drop_newest' | 'grow'.
        on_change:
            Iterable of callbacks receiving (event, stack). If a string 'print'
            is included, a built-in printer is attached.
        """
        self._data: List[T] = list(items)
        self._track = bool(track_minmax)
        self._maxsize = maxsize
        self._overflow = OverflowStrategy(overflow)

        # Auxiliary stacks for O(1) min/max when tracking is enabled.
        self._mins: List[T] = []
        self._maxs: List[T] = []

        # Event subscribers
        self._hooks: List[Callable[[ChangeEvent, "Stack[T]"], None]] = []
        if on_change:
            for h in on_change:
                if isinstance(h, str) and h == "print":
                    self._hooks.append(lambda ev, s: print(f"[stack-lab] {ev:>5} | size={len(s)} top={s._data[-1] if s._data else None}"))
                elif callable(h):
                    self._hooks.append(h)

        # Initialize min/max tracking based on initial items.
        if self._track:
            for x in self._data:
                self._push_minmax(x)

        # Transaction state (private)
        self._in_tx: bool = False
        self._tx_log: List[Tuple[str, Any]] = []

    # -------------------------- core helpers --------------------------
    @property
    def is_empty(self) -> bool:
        """True if the stack has no elements."""
        return not self._data

    def __len__(self) -> int:  # allows len(stack)
        return len(self._data)

    def __iter__(self) -> Iterator[T]:  # iterate bottom→top
        return iter(self._data)

    def __reversed__(self) -> Iterator[T]:  # iterate top→bottom
        return reversed(self._data)

    def __contains__(self, item: T) -> bool:
        return item in self._data

    def __repr__(self) -> str:
        return (
            f"Stack({self._data!r}, track_minmax={self._track}, "
            f"maxsize={self._maxsize}, overflow='{self._overflow.value}')"
        )

    def _emit(self, ev: ChangeEvent) -> None:
        for h in list(self._hooks):
            try:
                h(ev, self)
            except Exception:
                # Observers must not break core behavior
                pass

    def _enforce_capacity_on_push(self) -> None:
        if self._maxsize is None:
            return
        if len(self._data) < self._maxsize:
            return

        if self._overflow == OverflowStrategy.ERROR:
            raise StackCapacityError(f"Stack capacity {self._maxsize} reached")
        elif self._overflow == OverflowStrategy.DROP_OLDEST:
            # Drop from bottom; rebuild min/max stacks for correctness.
            if self._data:
                self._data.pop(0)
            if self._track:
                self._rebuild_minmax()
        elif self._overflow == OverflowStrategy.DROP_NEWEST:
            # Refuse the incoming push by raising a sentinel error
            raise StackCapacityError("DropNewest: incoming item refused")
        elif self._overflow == OverflowStrategy.GROW:
            # Do nothing: effectively unbounded
            pass

    def _push_minmax(self, item: T) -> None:
        if not self._mins:
            self._mins.append(item)
            self._maxs.append(item)
        else:
            self._mins.append(item if item <= self._mins[-1] else self._mins[-1])
            self._maxs.append(item if item >= self._maxs[-1] else self._maxs[-1])

    def _pop_minmax(self) -> None:
        if self._mins:
            self._mins.pop()
        if self._maxs:
            self._maxs.pop()

    def _rebuild_minmax(self) -> None:
        self._mins.clear()
        self._maxs.clear()
        if self._track:
            for x in self._data:
                self._push_minmax(x)

    # -------------------------- core API --------------------------
    def push(self, item: T) -> None:
        """Push an item onto the top (right side)."""
        # Capacity handling
        try:
            self._enforce_capacity_on_push()
        except StackCapacityError as e:
            if "DropNewest" in str(e):
                return  # refuse incoming element (no-op)
            raise

        self._data.append(item)
        if self._track:
            self._push_minmax(item)

        if self._in_tx:
            # Record that we pushed (for rollback we will pop)
            self._tx_log.append(("push", None))

        self._emit("push")

    def push_many(self, items: Iterable[T]) -> None:
        """Push many items in order."""
        for x in items:
            self.push(x)

    def pop(self) -> T:
        """Pop and return the top item. Raises StackEmptyError if empty."""
        if self.is_empty:
            raise StackEmptyError("pop from empty stack")
        x = self._data.pop()
        if self._track:
            self._pop_minmax()

        if self._in_tx:
            # Record the popped value so rollback can restore it
            self._tx_log.append(("pop", x))

        self._emit("pop")
        return x

    def pop_many(self, k: int) -> List[T]:
        """
        Pop up to k items (or fewer if the stack has less).
        Returns items in the order they were popped (top-first).
        """
        if k < 0:
            raise ValueError("k must be >= 0")
        out: List[T] = []
        for _ in range(min(k, len(self._data))):
            out.append(self.pop())
        return out

    def peek(self) -> T:
        """Return top item without removing it. Raises StackEmptyError if empty."""
        if self.is_empty:
            raise StackEmptyError("peek from empty stack")
        return self._data[-1]

    def safe_peek(self) -> Optional[T]:
        """Return top item or None if empty."""
        return self._data[-1] if self._data else None

    def clear(self) -> None:
        """Remove all items."""
        self._data.clear()
        self._mins.clear()
        self._maxs.clear()

        if self._in_tx:
            self._tx_log.append(("clear", None))

        self._emit("clear")

    # -------------------------- min/max --------------------------
    def min(self) -> T:
        """O(1) minimum (requires track_minmax=True and non-empty)."""
        if not self._track or self.is_empty:
            raise StackError("min() requires track_minmax=True and non-empty stack")
        return self._mins[-1]

    def max(self) -> T:
        """O(1) maximum (requires track_minmax=True and non-empty)."""
        if not self._track or self.is_empty:
            raise StackError("max() requires track_minmax=True and non-empty stack")
        return self._maxs[-1]

    # -------------------------- transactions --------------------------
    def begin(self) -> None:
        """Begin a transaction; later call commit() or rollback()."""
        if self._in_tx:
            raise StackTransactionError("transaction already active")
        self._in_tx = True
        self._tx_log.clear()

    def commit(self) -> None:
        """Commit current transaction; clears the log."""
        if not self._in_tx:
            return
        self._in_tx = False
        self._tx_log.clear()

    def rollback(self) -> None:
        """
        Roll back operations performed since begin().
        Notes:
          - push => undone by pop()
          - pop  => undone by re-push of the popped payload
          - clear=> cannot be perfectly restored (we avoid restoring here)
        """
        if not self._in_tx:
            return
        while self._tx_log:
            op, payload = self._tx_log.pop()
            if op == "push":
                if not self.is_empty:
                    # pop will also update min/max and emit event
                    self.pop()
            elif op == "pop":
                # re-insert the popped payload; use a direct push bypassing capacity
                try:
                    self.push(payload)  # obey capacity strategy
                except StackCapacityError:
                    # If capacity refuses, last resort insert at top
                    self._data.append(payload)
                    if self._track:
                        self._push_minmax(payload)
                    self._emit("push")
            elif op == "clear":
                # We don't attempt restoring the pre-clear state (log-free design).
                pass
        self._in_tx = False

    def transaction(self):
        """
        Context manager for transactions.

        Example:
        >>> s = Stack(1, 2, 3)
        >>> with s.transaction() as tx:
        ...     tx.push(10)
        ...     if True:
        ...         raise RuntimeError("fail")
        Traceback (most recent call last):
            ...
        RuntimeError: fail
        """
        class _Ctx:
            def __init__(self, stk: "Stack[T]") -> None:
                self.stk = stk
            def __enter__(self) -> "Stack[T]":
                self.stk.begin()
                return self.stk
            def __exit__(self, exc_type, exc, tb) -> bool:
                if exc:
                    self.stk.rollback()
                else:
                    self.stk.commit()
                # Propagate exception if any
                return False
        return _Ctx(self)

    # -------------------------- functional & utilities --------------------------
    def to_list(self) -> List[T]:
        """Return a shallow copy of internal list (bottom→top)."""
        return list(self._data)

    @classmethod
    def from_iterable(
        cls,
        it: Iterable[T],
        *,
        track_minmax: bool = False,
        maxsize: Optional[int] = None,
        overflow: OverflowStrategy = OverflowStrategy.ERROR,
        on_change: Optional[Iterable[Callable[[ChangeEvent, "Stack[T]"], None]] | Iterable[str]] = None,
    ) -> "Stack[T]":
        """Build a stack by pushing elements from an iterable."""
        s = cls(track_minmax=track_minmax, maxsize=maxsize, overflow=overflow, on_change=on_change)
        s.push_many(it)
        return s

    def copy(self) -> "Stack[T]":
        """Shallow copy of the stack (respects min/max tracking)."""
        s = Stack[T](track_minmax=self._track, maxsize=self._maxsize, overflow=self._overflow)
        s._data = self._data.copy()
        if self._track:
            s._rebuild_minmax()
        return s

    clone = copy  # alias

    def rotate(self, k: int) -> None:
        """
        Rotate the stack by k steps (positive: move top→bottom repeatedly).
        Example (top on right):
            [1,2,3,4], rotate(+1) -> [1,2,3,4] where 4 moves to bottom => [4,1,2,3]
        """
        n = len(self._data)
        if n == 0:
            return
        k %= n
        if k == 0:
            return
        # top is rightmost; rotate by slicing
        self._data = self._data[-k:] + self._data[:-k]
        if self._track:
            self._rebuild_minmax()

    def unique(self, *, keep: Literal["first", "last"] = "last") -> None:
        """
        Deduplicate items preserving order. Default keeps the last occurrence
        (so topmost duplicates survive). Use keep="first" to keep earliest.
        """
        seen = set()
        if keep == "last":
            # Traverse top→bottom so last occurrence is first seen
            out: List[T] = []
            for x in reversed(self._data):
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            out.reverse()
            self._data = out
        elif keep == "first":
            out = []
            for x in self._data:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            self._data = out
        else:
            raise ValueError("keep must be 'first' or 'last'")
        if self._track:
            self._rebuild_minmax()

    def count(self, item: T) -> int:
        """Count occurrences of `item` in the stack."""
        return self._data.count(item)

    def find(self, item: T) -> Optional[int]:
        """
        Return 0-based index from bottom (left) if found, else None.
        Note: this is Python list index semantics, not distance from top.
        """
        try:
            return self._data.index(item)
        except ValueError:
            return None

    def map_new(self, fn: Callable[[T], T]) -> "Stack[T]":
        """
        Functional map: returns a NEW Stack where each item is fn(item).
        Min/max tracking is disabled by default since mapping may break order.
        """
        return Stack.from_iterable(map(fn, self._data))

    def filter_new(self, pred: Callable[[T], bool]) -> "Stack[T]":
        """
        Functional filter: returns a NEW Stack containing items where pred(item) is True.
        """
        return Stack.from_iterable(x for x in self._data if pred(x))

    # -------------------------- snapshot / restore --------------------------
    def snapshot(self) -> Snapshot[T]:
        """Take an immutable snapshot of the stack contents."""
        return Snapshot(tuple(self._data), self._track)

    def restore(self, snap: Snapshot[T]) -> None:
        """
        Restore the stack to a previous snapshot.
        """
        self._data = list(snap.items)
        self._track = bool(snap.track_minmax)
        self._rebuild_minmax()

    # -------------------------- observers --------------------------
    def add_observer(self, cb: Callable[[ChangeEvent, "Stack[T]"], None]) -> None:
        """Subscribe to change events ('push', 'pop', 'clear')."""
        if not callable(cb):
            raise TypeError("observer must be callable")
        self._hooks.append(cb)

    def remove_observer(self, cb: Callable[[ChangeEvent, "Stack[T]"], None]) -> None:
        """Unsubscribe an observer; ignores if not present."""
        try:
            self._hooks.remove(cb)
        except ValueError:
            pass
