from itertools import groupby
from typing import Dict, List, Optional, Tuple

from bokeh.models import ColumnDataSource, RangeSlider, TextInput, Toggle
from sqlalchemy.engine import Row

DATE_TIME_FORMAT = "{%Y-%m-%d %H:%M:%S}"


def _group_stat(
    results: List[Row],
    stat_type: str,
    initial_key: Optional[str] = None,
) -> Tuple[ColumnDataSource, Dict[str, ColumnDataSource]]:
    """Group anime scores or anime view counts"""

    sources_dict = dict()
    for g_id, (sn, group_iter) in enumerate(groupby(results, key=lambda x: x[0])):
        group = list(group_iter)
        name = group[0][1]

        if (initial_key and initial_key == name) or (not initial_key and g_id == 0):
            first_data_source = ColumnDataSource(
                {
                    stat_type: [row[2] for row in group],
                    "insert_times": [row[3] for row in group],
                }
            )

        if name in sources_dict:
            name += " *"

        sources_dict[name] = ColumnDataSource(
            {
                stat_type: [row[2] for row in group],
                "insert_times": [row[3] for row in group],
            }
        )

    return first_data_source, sources_dict


def _get_filter_tools(
    max_view_count,
) -> Tuple[TextInput, Toggle, Toggle, RangeSlider, RangeSlider]:
    text_input = TextInput(placeholder="動畫名稱", height_policy="min")
    only_new_toggle = Toggle(
        label="只顯示新番",
        button_type="default",
        active=False,
        height_policy="min",
        width_policy="min",
    )
    ignore_wip_toggle = Toggle(
        label="不顯示統計中",
        button_type="default",
        active=False,
        height_policy="min",
        width_policy="min",
    )
    view_counter_silider = RangeSlider(
        start=-1,
        end=max_view_count,
        value=(-1, max_view_count),
        step=1,
        title="觀看人次",
        margin=(2, 10, 5, 10),
    )
    score_slider = RangeSlider(
        start=-1, end=10, value=(-1, 10), step=0.1, title="評分", margin=(2, 10, 5, 10)
    )
    return (
        text_input,
        only_new_toggle,
        ignore_wip_toggle,
        view_counter_silider,
        score_slider,
    )
