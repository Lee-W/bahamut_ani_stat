from itertools import groupby
from typing import Dict, List, Optional, Tuple

from bokeh.models import ColumnDataSource
from sqlalchemy.engine import Row

DATE_TIME_FORMAT = "{%Y-%m-%d %H:%M:%S}"


def _group_stat(
    results: List[Row], stat_type: str, initial_key: Optional[str] = None,
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
