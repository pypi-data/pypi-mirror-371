"""scoped-context."""

from __future__ import annotations

__all__ = ["ScopedContext", "get_context_stack", "get_current_context"]

import queue
import sys
import threading

if sys.version_info >= (3, 11):
    from typing import TYPE_CHECKING, ClassVar, Self
else:
    from typing import TYPE_CHECKING, ClassVar

    from typing_extensions import Self

if TYPE_CHECKING:
    from types import TracebackType


class NoContextError(Exception):
    """Exception raised when there is no current context."""


class ScopedContext:
    """A mixin class for context management."""

    # Thread-local storage for each subclass
    _thread_local: ClassVar[threading.local]

    # Thread-local storage shared across all subclasses
    _thread_local_classwide: ClassVar[threading.local] = threading.local()

    def __init_subclass__(cls, *args: object, **kwargs: object) -> None:
        """Initialize the class-specific thread-local storage when a subclass is created."""
        super().__init_subclass__(*args, **kwargs)
        cls._thread_local = threading.local()

    @classmethod
    def _stack(cls) -> queue.LifoQueue[Self]:
        if not hasattr(cls._thread_local, "stack"):
            cls._thread_local.stack = queue.LifoQueue()
        return cls._thread_local.stack  # type: ignore[no-any-return]

    @classmethod
    def _classwide_stack(cls) -> queue.LifoQueue[ScopedContext]:
        if not hasattr(cls._thread_local_classwide, "stack"):
            cls._thread_local_classwide.stack = queue.LifoQueue()
        return cls._thread_local_classwide.stack  # type: ignore[no-any-return]

    @classmethod
    def context_stack(cls) -> list[Self]:
        """Get the stack queue for the current context.

        The last item of the returned list is the current context.
        """
        return cls._stack().queue

    @classmethod
    def _classwide_context_stack(
        cls,
        class_or_tuple: type[ScopedContext] | tuple[type[ScopedContext], ...] | None = None,
    ) -> list[ScopedContext]:
        """Get the classwide stack queue for the current context.

        The last item of the returned list is the current classwide context.

        If class_or_tuple is provided, filter the queue to only include instances of the specified class or classes.
        """
        if class_or_tuple is not None:
            return [item for item in cls._classwide_stack().queue if isinstance(item, class_or_tuple)]
        return cls._classwide_stack().queue

    @classmethod
    def current(cls) -> Self:
        """Get the current context of the class."""
        if cls._stack().qsize() == 0:
            msg = "No current context"
            raise NoContextError(msg)
        return cls._stack().queue[-1]

    @classmethod
    def _current_classwide(
        cls,
        class_or_tuple: type[ScopedContext] | tuple[type[ScopedContext], ...] | None = None,
    ) -> ScopedContext:
        """Get the current classwide context.

        If class_or_tuple is provided, filter the queue to only include instances of the specified class or classes.
        """
        queue = cls._classwide_context_stack(class_or_tuple)
        if not queue:
            msg = "No current classwide context"
            raise NoContextError(msg)
        return queue[-1]

    def __enter__(self) -> Self:
        """Enter the context."""
        self._stack().put(self, block=False)
        self._classwide_stack().put(self, block=False)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the context."""
        self._stack().get(block=False)
        self._classwide_stack().get(block=False)


def get_current_context(
    class_or_tuple: type[ScopedContext] | tuple[type[ScopedContext], ...] | None = None,
) -> ScopedContext:
    """Get the current classwide context.

    If class_or_tuple is provided, filter the queue to only include instances of the specified class or classes.
    """
    queue = ScopedContext._classwide_context_stack(class_or_tuple)  # noqa: SLF001
    if not queue:
        msg = "No current classwide context"
        raise NoContextError(msg)
    return queue[-1]


def get_context_stack(
    class_or_tuple: type[ScopedContext] | tuple[type[ScopedContext], ...] | None = None,
) -> list[ScopedContext]:
    """Get the classwide stack queue for the current context.

    The last item of the returned list is the current classwide context.

    If class_or_tuple is provided, filter the queue to only include instances of the specified class or classes.
    """
    if class_or_tuple is not None:
        return [item for item in ScopedContext._classwide_stack().queue if isinstance(item, class_or_tuple)]  # noqa: SLF001
    return ScopedContext._classwide_stack().queue  # noqa: SLF001
