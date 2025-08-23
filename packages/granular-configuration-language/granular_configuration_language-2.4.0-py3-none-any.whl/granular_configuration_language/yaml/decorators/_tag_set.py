from __future__ import annotations

import collections.abc as tabc
import sys
import typing as typ
from collections import OrderedDict

from granular_configuration_language.exceptions import ErrorWhileLoadingTags
from granular_configuration_language.yaml.decorators._base import Tag, TagConstructor

if sys.version_info >= (3, 12):
    from typing import override
elif typ.TYPE_CHECKING:
    from typing_extensions import override
else:

    def override(func: tabc.Callable) -> tabc.Callable:
        return func


class TagSet(tabc.Iterable[TagConstructor], tabc.Container[str]):
    def __init__(self, tags: tabc.Iterable[TagConstructor]) -> None:
        self.__state: OrderedDict[Tag, TagConstructor] = OrderedDict()

        for tc in tags:
            tag = tc.tag
            if tag in self.__state:
                raise ErrorWhileLoadingTags(
                    f"Tag is already defined. `{repr(tc)}` attempted to replace `{repr(self.__state[tag])}`"
                )
            else:
                self.__state[tag] = tc

    @override
    def __contains__(self, x: typ.Any) -> bool:
        return x in self.__state

    @override
    def __iter__(self) -> tabc.Iterator[TagConstructor]:
        return iter(self.__state.values())

    @override
    def __repr__(self) -> str:
        return f"TagSet{{{','.join(sorted(self.__state.keys()))}}}"

    def has_tags(self, *tags: Tag | str) -> bool:
        return all(map(self.__contains__, tags))

    def does_not_have_tags(self, *tags: Tag | str) -> bool:
        return not any(map(self.__contains__, tags))

    def get_subset(self, *select: str) -> TagSet:
        def subset() -> tabc.Iterator[TagConstructor]:
            for tag in self:
                if tag.tag in select:
                    yield tag

        return TagSet(subset())

    def get_difference(self, *select: str) -> TagSet:
        def subset() -> tabc.Iterator[TagConstructor]:
            for tag in self:
                if tag.tag not in select:
                    yield tag

        return TagSet(subset())
