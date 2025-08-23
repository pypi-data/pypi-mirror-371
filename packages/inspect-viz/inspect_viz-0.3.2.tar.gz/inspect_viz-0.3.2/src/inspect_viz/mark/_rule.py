from typing import Any

from typing_extensions import Unpack

from .._core import Data, Param, Selection
from .._core.types import Interval
from .._util.marshall import dict_remove_none
from ._channel import ChannelIntervalSpec, ChannelSpec
from ._mark import Mark
from ._options import MarkOptions
from ._types import Marker
from ._util import column_param


def rule_x(
    data: Data | None = None,
    x: ChannelSpec | Param | None = None,
    y: ChannelIntervalSpec | Param | None = None,
    y1: ChannelSpec | Param | None = None,
    y2: ChannelSpec | Param | None = None,
    filter_by: Selection | None = None,
    interval: Interval | None = None,
    marker: Marker | bool | Param | None = None,
    marker_start: Marker | bool | Param | None = None,
    marker_mid: Marker | bool | Param | None = None,
    marker_end: Marker | bool | Param | None = None,
    inset: float | Param | None = None,
    **options: Unpack[MarkOptions],
) -> Mark:
    """A ruleX mark that draws horizontal rule lines.

    RuleX marks are horizontal lines that span the full extent of the plot area,
    typically used for reference lines, grid lines, or highlighting specific values.

    Args:
        data: The data source for the mark.
        x: The horizontal position channel, typically bound to the *x* scale.
        y: The vertical position channel, typically bound to the *y* scale.
        y1: The primary (starting, often bottom) vertical position of the tick; a channel bound to the *y* scale.
        y2: The secondary (ending, often top) vertical position of the tick; a channel bound to the *y* scale.
        filter_by: A selection to filter the data.
        interval: How to convert a continuous value into an interval.
        marker: The marker symbol to use at all positions along the rule.
        marker_start: The marker symbol to use at the start of the rule.
        marker_mid: The marker symbol to use at the middle of the rule.
        marker_end: The marker symbol to use at the end of the rule.
        inset: Set top and bottom insets.
        **options: Additional mark options from MarkOptions.

    Returns:
        A ruleX mark.
    """
    config: dict[str, Any] = dict_remove_none(
        dict(
            data=data._plot_from(filter_by) if data else None,
            x=column_param(data, x),
            y=column_param(data, y),
            y1=column_param(data, y1),
            y2=column_param(data, y2),
            interval=interval,
            marker=marker,
            markerStart=marker_start,
            markerMid=marker_mid,
            markerEnd=marker_end,
            inset=inset,
        )
    )

    return Mark("ruleX", config, options)


def rule_y(
    data: Data | None = None,
    y: ChannelSpec | Param | None = None,
    x: ChannelIntervalSpec | Param | None = None,
    x1: ChannelSpec | Param | None = None,
    x2: ChannelSpec | Param | None = None,
    filter_by: Selection | None = None,
    interval: Interval | None = None,
    marker: Marker | bool | Param | None = None,
    marker_start: Marker | bool | Param | None = None,
    marker_mid: Marker | bool | Param | None = None,
    marker_end: Marker | bool | Param | None = None,
    inset: float | Param | None = None,
    **options: Unpack[MarkOptions],
) -> Mark:
    """A ruleY mark that draws vertical rule lines.

    RuleY marks are vertical lines that span the full extent of the plot area,
    typically used for reference lines, grid lines, or highlighting specific values.

    Args:
        data: The data source for the mark.
        y: The vertical position channel, typically bound to the *y* scale.
        x: The horizontal position channel, typically bound to the *x* scale.
        x1: The primary (starting, often left) horizontal position of the tick; a channel bound to the *x* scale.
        x2: The secondary (ending, often right) horizontal position of the tick; a channel bound to the *x* scale.
        filter_by: A selection to filter the data.
        interval: How to convert a continuous value into an interval.
        marker: The marker symbol to use at all positions along the rule.
        marker_start: The marker symbol to use at the start of the rule.
        marker_mid: The marker symbol to use at the middle of the rule.
        marker_end: The marker symbol to use at the end of the rule.
        inset: Set left and right insets.
        **options: Additional mark options from MarkOptions.

    Returns:
        A ruleY mark.
    """
    config: dict[str, Any] = dict_remove_none(
        dict(
            data=data._plot_from(filter_by) if data else None,
            y=column_param(data, y),
            x=column_param(data, x),
            x1=column_param(data, x1),
            x2=column_param(data, x2),
            interval=interval,
            marker=marker,
            markerStart=marker_start,
            markerMid=marker_mid,
            markerEnd=marker_end,
            inset=inset,
        )
    )

    return Mark("ruleY", config, options)
