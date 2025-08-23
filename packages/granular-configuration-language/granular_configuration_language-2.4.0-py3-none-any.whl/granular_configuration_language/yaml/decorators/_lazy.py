from __future__ import annotations

import collections.abc as tabc
import typing as typ

from granular_configuration_language.yaml.classes import RT, LazyEval, LoadOptions, Root, StateHolder, T, Tag
from granular_configuration_language.yaml.decorators._lazy_eval import LazyEvalBasic, LazyEvalWithRoot
from granular_configuration_language.yaml.decorators._tag_tracker import tracker


def as_lazy(func: tabc.Callable[[T], RT], /) -> tabc.Callable[[Tag, T, StateHolder], LazyEval[RT]]:
    """Wraps the "Tag" function in a :py:class:`~.LazyEval`, so that the function being wrapped is run just-in-time.

    .. admonition:: Positional Parameters for "Tag" function
        :class: hint

        1. (:py:class:`~granular_configuration_language.yaml.classes.T`) - YAML value

    :param ~collections.abc.Callable[[T], RT] func: Function to be wrapped

    :returns: Wrapped Function
    :rtype: ~collections.abc.Callable[[Tag, T, StateHolder], LazyEval[RT]]

    :example:
        .. code-block:: python

            @string_tag(Tag("!Tag"))
            @as_lazy
            def tag(value: str) -> Any: ...
    """

    @tracker.wraps(func)
    def lazy_wrapper(tag: Tag, value: T, state: StateHolder) -> LazyEvalBasic[RT]:
        return LazyEvalBasic(tag, lambda: func(value))

    return lazy_wrapper


def as_lazy_with_load_options(
    func: tabc.Callable[[T, LoadOptions], RT],
) -> tabc.Callable[[Tag, T, StateHolder], LazyEval[RT]]:
    """Wraps the "Tag" function in a :py:class:`~.LazyEval`, so that the function being wrapped is run just-in-time.

    .. admonition:: Positional Parameters for "Tag" function
        :class: hint

        1. (:py:class:`~granular_configuration_language.yaml.classes.T`) - YAML value
        2. (:py:class:`.LoadOptions`) - A :py:class:`.LoadOptions` instance

    :param ~collections.abc.Callable[[T, LoadOptions], RT] func: Function to be wrapped

    :returns: Wrapped Function
    :rtype: ~collections.abc.Callable[[Tag, T, StateHolder], LazyEval[RT]]

    :example:
        .. code-block:: python

            @string_tag(Tag("!Tag"))
            @as_lazy_with_load_options
            def tag(value: str, options: LoadOptions) -> Any: ...
    """

    @tracker.wraps(func)
    def lazy_wrapper(tag: Tag, value: T, state: StateHolder) -> LazyEvalBasic[RT]:
        options = state.options
        return LazyEvalBasic(tag, lambda: func(value, options))

    return lazy_wrapper


@typ.overload
def as_lazy_with_root(func: tabc.Callable[[T, Root], RT], /) -> tabc.Callable[[Tag, T, StateHolder], LazyEval[RT]]: ...


@typ.overload
def as_lazy_with_root(
    *, needs_root_condition: tabc.Callable[[T], bool]
) -> tabc.Callable[[tabc.Callable[[T, Root], RT]], tabc.Callable[[Tag, T, StateHolder], LazyEval[RT]]]: ...


def as_lazy_with_root(
    func: tabc.Callable[[T, Root], RT] | None = None, /, *, needs_root_condition: tabc.Callable[[T], bool] | None = None
) -> (
    tabc.Callable[[Tag, T, StateHolder], LazyEval[RT]]
    | tabc.Callable[[tabc.Callable[[T, Root], RT]], tabc.Callable[[Tag, T, StateHolder], LazyEval[RT]]]
):
    r"""Wraps the "Tag" function in a :py:class:`~.LazyEval`, so that the function being wrapped is run just-in-time.

    .. admonition:: Positional Parameters for "Tag" function
        :class: hint

        1. (:py:class:`~granular_configuration_language.yaml.classes.T`) -- YAML value
        2. (:py:type:`~granular_configuration_language.yaml.classes.Root`) -- Configuration Root

    .. admonition:: Documentation Issue
        :class: caution

        ``sphinx.ext.autodoc`` isn't exposing the :py:func:`typing.overload`. See the example for a clearer type signatures

        .. admonition:: Typing Stub
            :class: note
            :collapsible: closed

            .. code-block:: python

                # Decorator
                # Uses as: ``@as_lazy_with_root``
                @overload
                def as_lazy_with_root(
                    func: Callable[[T, Root], RT],
                ) -> Callable[[Tag, T, StateHolder], LazyEval[RT]]: ...


                # Decorator Factory
                # Uses as: ``@as_lazy_with_root(needs_root_condition=condition)``
                @overload
                def as_lazy_with_root(
                    *, needs_root_condition: Callable[[T], bool]
                ) -> Callable[
                    [Callable[[T, Root], RT]],
                    Callable[[Tag, T, StateHolder], LazyEval[RT]],
                ]: ...

    :param ~collections.abc.Callable[[T, Root], RT] func:
        Function to be wrapped
    :param ~collections.abc.Callable[[T], bool], optional needs_root_condition:
        - A Boolean Condition used to test the raw YAML value.

            - If :py:data:`True`, :py:type:`~granular_configuration_language.yaml.classes.Root` is set to the Configuration Root.
            - If :py:data:`False`, :py:type:`~granular_configuration_language.yaml.classes.Root` is set to :py:data:`None`.

        - Used as a decorator factory:

            - ``@as_lazy_with_root(needs_root_condition= ... )``

    :returns: Wrapped Function
    :rtype: ~collections.abc.Callable[[Tag, T, StateHolder], LazyEval[RT]]

    :example:
        .. code-block:: python

            # Typical usage
            @string_tag(Tag("!Tag"))
            @as_lazy_with_root
            def tag(value: str, root: Root) -> Any: ...


            # Using `needs_root_condition`
            @string_tag(Tag("!Tag"))
            @as_lazy_with_root(needs_root_condition=interpolation_needs_ref_condition)
            @interpolate_value_with_ref
            def tag(value: str, root: Root) -> Any: ...
    """

    def decorator_generator(
        func: tabc.Callable[[T, Root], RT],
        /,
    ) -> tabc.Callable[[Tag, T, StateHolder], LazyEval[RT]]:
        @tracker.wraps(func, needs_root_condition=needs_root_condition)
        def lazy_wrapper(tag: Tag, value: T, state: StateHolder) -> LazyEval[RT]:
            if (needs_root_condition is None) or needs_root_condition(value):
                return LazyEvalWithRoot(tag, state.lazy_root_obj, lambda root: func(value, root))
            else:
                return LazyEvalBasic(tag, lambda: func(value, None))

        return lazy_wrapper

    if func is None:
        return decorator_generator
    else:
        return decorator_generator(func)


def as_lazy_with_root_and_load_options(
    func: tabc.Callable[[T, Root, LoadOptions], RT],
    /,
) -> tabc.Callable[[Tag, T, StateHolder], LazyEval[RT]]:
    """Wraps the "Tag" function in a :py:class:`~.LazyEval`, so that the function being wrapped is run just-in-time.

    .. admonition:: Positional Parameters for "Tag" function
        :class: hint

        1. (:py:class:`~granular_configuration_language.yaml.classes.T`) -- YAML value
        2. (:py:type:`~granular_configuration_language.yaml.classes.Root`) -- Configuration root
        3. (:py:class:`.LoadOptions`) -- A :py:class:`.LoadOptions` instance

    :param ~collections.abc.Callable[[T, ~granular_configuration_language.yaml.classes.Root, LoadOptions], RT] func: Function to be wrapped

    :returns: Wrapped Function
    :rtype: ~collections.abc.Callable[[Tag, T, StateHolder], LazyEval[RT]]

    :example:
        .. code-block:: python

            @string_tag(Tag("!Tag"))
            @as_lazy_with_root_and_load_options
            def tag(value: str, root: Root, options: LoadOptions) -> Any: ...
    """

    @tracker.wraps(func)
    def lazy_wrapper(tag: Tag, value: T, state: StateHolder) -> LazyEvalWithRoot[RT]:
        options = state.options
        return LazyEvalWithRoot(tag, state.lazy_root_obj, lambda root: func(value, root, options))

    return lazy_wrapper


def as_not_lazy(func: tabc.Callable[[T], RT], /) -> tabc.Callable[[Tag, T, StateHolder], RT]:
    """Wraps the "Tag" function, but does not make it lazy. The function being wrapped is run at load time.

    .. admonition:: Positional Parameters for "Tag" function
        :class: hint

        1. (:py:class:`~granular_configuration_language.yaml.classes.T`) - YAML value

    :param ~collections.abc.Callable[[T], RT] func: Function to be wrapped

    :returns: Wrapped Function
    :rtype: ~collections.abc.Callable[[Tag, T, StateHolder], LazyEval[RT]]

    :example:
        .. code:: python

            @string_tag(Tag("!Tag"))
            @as_not_lazy
            def tag(value: str) -> Any:
                ...
    """

    @tracker.wraps(func, is_not_lazy=True)
    def lazy_wrapper(tag: Tag, value: T, state: StateHolder) -> RT:
        return func(value)

    return lazy_wrapper
