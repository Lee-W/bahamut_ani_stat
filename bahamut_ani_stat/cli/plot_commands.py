from __future__ import annotations

import importlib.resources
import json
import os
from itertools import groupby

import click
import pandas as pd
import sqlalchemy
from bokeh.io import output_file, save
from bokeh.layouts import column, row
from bokeh.models import (  # type: ignore[attr-defined]
    CDSView,
    ColumnDataSource,
    CustomJS,
    CustomJSFilter,
    DataTable,
    DateFormatter,
    HTMLTemplateFormatter,
    NumeralTickFormatter,
    Range1d,
    Select,
    TableColumn,
)
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import functions as sql_func

from bahamut_ani_stat.db import models
from bahamut_ani_stat.db.utils import latest_score_cte, latest_view_count_cte
from bahamut_ani_stat.plot.utils import DATE_TIME_FORMAT, _get_filter_tools


@click.group(name="plot")
def plot_command_group() -> None:
    pass


@plot_command_group.command(name="premium-rate")
@click.argument("db-uri")
@click.argument("output-filename", default="premium-rate.html")
def plot_premium_rate_command(db_uri: str, output_filename: str) -> None:
    """Plot premium rate as trend chart"""
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = select(models.PremiumRate)
        results = session.execute(stmt).scalars().all()
        data = {row.insert_time: row.premium_rate for row in results}

    pr_series = pd.Series(data).interpolate(method="pad")

    output_file(filename=output_filename, title="動畫瘋付費比例趨勢")
    p = figure(  # type: ignore[call-arg]
        title="動畫瘋付費比例趨勢",
        x_axis_label="記錄時間",
        y_axis_label="付費比例",
        x_axis_type="datetime",
    )
    p.add_tools(
        HoverTool(
            tooltips=[("rate: ", "@y{1.11}"), ("date: ", f"@x{DATE_TIME_FORMAT}")],
            formatters={"@x": "datetime"},
        )
    )
    p.line(pr_series.index, pr_series.values)
    save(p)
    click.echo(f"Export premium plot to {output_filename}")


@plot_command_group.command(name="anime")
@click.argument("db-uri")
@click.argument("output-filename", default="anime.html")
def plot_anime_command(db_uri: str, output_filename: str) -> None:
    """Plot anime data from database as an interactive data table"""
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = (
            select(
                models.Anime.sn,
                models.Anime.name,
                models.Anime.release_time,
                models.Anime.is_new,
                latest_view_count_cte.c.view_count,
                latest_score_cte.c.score,
            )
            .join(latest_view_count_cte)
            .outerjoin(latest_score_cte)
            .order_by(latest_view_count_cte.c.view_count.desc())
        )
        results = session.execute(stmt)
        df = pd.DataFrame(results.fetchall(), columns=results.keys())
        df["score"] = df["score"].fillna(-1)
        column_sources = df.to_dict(orient="list")

        stmt = select(sql_func.max(models.AnimeViewCount.view_count))
        max_view_count: int = session.execute(stmt).scalars().first() or 0

    data_source = ColumnDataSource(data=column_sources)

    output_file(filename=output_filename, title="動畫瘋所有動畫")

    emit_js = CustomJS(args={"data_source": data_source}, code="data_source.change.emit()")

    (
        text_input,
        only_new_toggle,
        ignore_wip_toggle,
        view_counter_silider,
        score_slider,
    ) = _get_filter_tools(max_view_count)

    text_input.js_on_change("value", emit_js)
    only_new_toggle.js_on_click(emit_js)
    ignore_wip_toggle.js_on_click(emit_js)
    view_counter_silider.js_on_change("value", emit_js)
    score_slider.js_on_change("value", emit_js)

    anime_js_filter = CustomJSFilter(
        args={
            "data_source": data_source,
            "score_slider": score_slider,
            "view_counter_silider": view_counter_silider,
            "only_new_toggle": only_new_toggle,
            "ignore_wip_toggle": ignore_wip_toggle,
            "text_input": text_input,
        },
        code=importlib.resources.files("bahamut_ani_stat.plot")
        .joinpath("static/datatable-anime-filter.js")
        .read_text(encoding="utf-8"),
    )
    view = CDSView(filter=anime_js_filter)
    columns = [
        TableColumn(field="name", title="動畫名稱"),
        TableColumn(field="score", title="評分"),
        TableColumn(field="view_count", title="觀看人次"),
        TableColumn(field="is_new", title="是否為新番"),
        TableColumn(field="release_time", title="動畫播出時間", formatter=DateFormatter()),
        TableColumn(
            field="sn",
            title="sn",
            formatter=HTMLTemplateFormatter(
                template="""
                    <a href="https://ani.gamer.com.tw/animeRef.php?sn=<%= value %>
                            "target="new">
                        <%= value %>
                    </a>"""
            ),
        ),
    ]
    data_table = DataTable(
        source=data_source,
        columns=columns,
        editable=True,
        reorderable=True,
        height_policy="max",
        width_policy="max",
        view=view,
    )
    result = column(
        column(row(text_input, only_new_toggle, ignore_wip_toggle), height=50),
        column(row(view_counter_silider, score_slider), height=50),
        data_table,
        sizing_mode="stretch_both",
    )
    save(result)
    click.echo(f"Export anime plot to {output_filename}")


@plot_command_group.command(name="anime-trend-data")
@click.argument("db-uri")
@click.argument("output-dir", default="docs/assets/data/anime_trend")
def plot_anime_trend_data_command(db_uri: str, output_dir: str) -> None:
    """Generate per-anime JSON files for lazy-loading in the trend chart"""
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        view_stmt = (
            select(
                models.Anime.sn,
                models.AnimeViewCount.view_count,
                models.AnimeViewCount.insert_time,
            )
            .join(models.AnimeViewCount)
            .order_by(models.Anime.sn, models.AnimeViewCount.insert_time)
        )
        view_rows = session.execute(view_stmt).fetchall()

        score_stmt = (
            select(
                models.Anime.sn,
                models.AnimeScore.score,
                models.AnimeScore.insert_time,
            )
            .join(models.AnimeScore)
            .order_by(models.Anime.sn, models.AnimeScore.insert_time)
        )
        score_rows = session.execute(score_stmt).fetchall()

    view_by_sn: dict[str, dict[str, list[object]]] = {}
    for sn, group in groupby(view_rows, key=lambda r: r[0]):
        rows = list(group)
        view_by_sn[sn] = {
            "view_counts": [r[1] for r in rows],
            "insert_times": [int(r[2].timestamp() * 1000) for r in rows],
        }

    score_by_sn: dict[str, dict[str, list[object]]] = {}
    for sn, group in groupby(score_rows, key=lambda r: r[0]):  # type: ignore[assignment]
        rows = list(group)
        score_by_sn[sn] = {
            "scores": [r[1] for r in rows],
            "insert_times": [int(r[2].timestamp() * 1000) for r in rows],
        }

    os.makedirs(output_dir, exist_ok=True)
    all_sn = set(view_by_sn) | set(score_by_sn)
    for sn in all_sn:
        payload = {
            "view_counts": view_by_sn.get(sn, {"view_counts": [], "insert_times": []}),
            "scores": score_by_sn.get(sn, {"scores": [], "insert_times": []}),
        }
        with open(os.path.join(output_dir, f"{sn}.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f)

    click.echo(f"Wrote {len(all_sn)} anime JSON files to {output_dir}")


@plot_command_group.command(name="anime-trend")
@click.argument("db-uri")
@click.argument("output-filename", default="anime-trend.html")
@click.option(
    "--data-path", default="assets/data/anime_trend", help="Relative path prefix for JSON data files"
)
def plot_anime_trend_command(db_uri: str, output_filename: str, data_path: str) -> None:
    """Plot the score and view count trend for new animes (lazy-loads per-anime JSON)"""
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = (
            select(
                models.Anime.sn,
                models.Anime.name,
                models.Anime.is_new,
                latest_view_count_cte.c.view_count,
                latest_score_cte.c.score,
            )
            .join(latest_view_count_cte)
            .outerjoin(latest_score_cte)
            .order_by(latest_view_count_cte.c.view_count.desc())
        )
        ani_results = session.execute(stmt)
        df = pd.DataFrame(ani_results.fetchall(), columns=ani_results.keys())
        df["score"] = df["score"].fillna(-1)
        column_sources = df.to_dict(orient="list")
        data_sources = ColumnDataSource(column_sources)

        stmt = select(sql_func.max(models.AnimeViewCount.view_count))
        max_view_count: int = session.execute(stmt).scalars().first() or 0

        # Fetch initial data for the first anime in the list
        first_sn: str = df["sn"].iloc[0] if not df.empty else ""
        first_name: str = df["name"].iloc[0] if not df.empty else ""

        view_stmt = (
            select(models.AnimeViewCount.view_count, models.AnimeViewCount.insert_time)
            .where(models.AnimeViewCount.anime_sn == first_sn)
            .order_by(models.AnimeViewCount.insert_time)
        )
        view_rows = session.execute(view_stmt).fetchall()

        score_stmt = (
            select(models.AnimeScore.score, models.AnimeScore.insert_time)
            .where(models.AnimeScore.anime_sn == first_sn)
            .order_by(models.AnimeScore.insert_time)
        )
        score_rows = session.execute(score_stmt).fetchall()

    name_to_sn: dict[str, str] = dict(zip(df["name"].tolist(), df["sn"].tolist()))
    anime_name_list: list[str] = df["name"].tolist()

    first_view_source = ColumnDataSource(
        {
            "view_counts": [r[0] for r in view_rows],
            "insert_times": [r[1] for r in view_rows],
        }
    )
    first_score_source = ColumnDataSource(
        {
            "scores": [r[0] for r in score_rows],
            "insert_times": [r[1] for r in score_rows],
        }
    )

    output_file(filename=output_filename, title="動畫瘋觀看、評分趨勢")

    view_pic = figure(x_axis_type="datetime")  # type: ignore[call-arg]
    view_pic.yaxis.formatter = NumeralTickFormatter(format="0,0")
    view_pic.add_tools(
        HoverTool(
            tooltips=[
                ("view count", "@view_counts"),
                ("date: ", f"@insert_times{DATE_TIME_FORMAT}"),
            ],
            formatters={"@insert_times": "datetime"},
        )
    )
    view_pic.line("insert_times", "view_counts", source=first_view_source)

    score_pic = figure(x_axis_type="datetime")  # type: ignore[call-arg]
    score_pic.line("insert_times", "scores", source=first_score_source)
    score_pic.y_range = Range1d(1, 5)  # type: ignore[arg-type]
    score_pic.add_tools(
        HoverTool(
            tooltips=[
                ("score", "@scores{1.1}"),
                ("date: ", f"@insert_times{DATE_TIME_FORMAT}"),
            ],
            formatters={"@insert_times": "datetime"},
        )
    )

    ani_select = Select(title="作品", value=first_name, options=anime_name_list)
    ani_select.js_on_change(
        "value",
        CustomJS(
            args={
                "view_source": first_view_source,
                "score_source": first_score_source,
                "name_to_sn": name_to_sn,
                "data_path": data_path,
            },
            code=importlib.resources.files("bahamut_ani_stat.plot")
            .joinpath("static/new-anime-source-update-dropdown.js")
            .read_text(encoding="utf-8"),
        ),
    )

    (
        text_input,
        only_new_toggle,
        ignore_wip_toggle,
        view_counter_silider,
        score_slider,
    ) = _get_filter_tools(max_view_count)
    filter_js = CustomJS(
        args={
            "ani_select": ani_select,
            "score_slider": score_slider,
            "view_counter_silider": view_counter_silider,
            "only_new_toggle": only_new_toggle,
            "ignore_wip_toggle": ignore_wip_toggle,
            "text_input": text_input,
            "data_source": data_sources,
        },
        code=importlib.resources.files("bahamut_ani_stat.plot")
        .joinpath("static/dropdown-anime-filter.js")
        .read_text(encoding="utf-8"),
    )

    text_input.js_on_change("value", filter_js)
    ignore_wip_toggle.js_on_click(filter_js)
    only_new_toggle.js_on_click(filter_js)
    view_counter_silider.js_on_change("value", filter_js)
    score_slider.js_on_change("value", filter_js)

    save(
        column(
            column(row(text_input, only_new_toggle, ignore_wip_toggle), height=50),
            column(row(view_counter_silider, score_slider), height=50),
            ani_select,
            row(view_pic, score_pic),
        )
    )
    click.echo(f"Export new anime view count trend to {output_filename}")
