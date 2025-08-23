from __future__ import annotations

import sys
from datetime import date, datetime
from functools import partial

from granular_configuration_language.yaml.decorators import Tag, as_lazy, interpolate_value_without_ref, string_tag

if sys.version_info >= (3, 11):
    date_fromisoformat = date.fromisoformat
    datetime_fromisoformat = datetime.fromisoformat
else:  # if sys.version_info
    from dateutil.parser import parse

    datetime_fromisoformat = partial(parse, yearfirst=True, dayfirst=False)
    date_fromisoformat = lambda value: datetime_fromisoformat(value).date()


@string_tag(Tag("!Date"), "Typer")
@as_lazy
@interpolate_value_without_ref
def date_(value: str) -> date:
    return date_fromisoformat(value)


@string_tag(Tag("!DateTime"), "Typer")
@as_lazy
@interpolate_value_without_ref
def datetime_(value: str) -> date:
    dt = datetime_fromisoformat(value)
    return dt
