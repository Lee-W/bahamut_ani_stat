import click
import pandas as pd
import pkg_resources
import sqlalchemy
from bokeh.io import output_file, save
from bokeh.layouts import column, row
from bokeh.models import (
    CDSView,
    ColumnDataSource,
    CustomJS,
    CustomJSFilter,
    DataTable,
    DateFormatter,
    HTMLTemplateFormatter,
    NumeralTickFormatter,
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
from bahamut_ani_stat.plot.utils import DATE_TIME_FORMAT, _get_filter_tools, _group_stat


@click.group(name="plot")
def plot_command_group():
    pass


@plot_command_group.command(name="premium-rate")
@click.argument("db-uri")
@click.argument("output-filename", default="premium-rate.html")
def plot_premium_rate_command(db_uri: str, output_filename: str):
    """Plot premium rate as trend chart"""
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = select(models.PremiumRate)
        results = session.execute(stmt).scalars().all()
        data = {row.insert_time: row.premium_rate for row in results}

    pr_series = pd.Series(data).interpolate(method="pad")

    output_file(filename=output_filename, title="動畫瘋付費比例趨勢")
    p = figure(
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
def plot_anime_command(db_uri: str, output_filename: str):
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
            .join(latest_score_cte)
            .order_by(latest_view_count_cte.c.view_count.desc())
        )
        results = session.execute(stmt)
        df = pd.DataFrame(results.fetchall(), columns=results.keys())
        column_sources = df.to_dict(orient="list")

        stmt = select(sql_func.max(models.AnimeViewCount.view_count))
        max_view_count = session.execute(stmt).scalars().first()

    data_source = ColumnDataSource(column_sources)

    output_file(filename=output_filename, title="動畫瘋所有動畫")

    emit_js = CustomJS(
        args={"data_source": data_source}, code="data_source.change.emit()"
    )

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
        code=pkg_resources.resource_string(
            "bahamut_ani_stat.plot", "static/datatable-anime-filter.js"
        ).decode("utf-8"),
    )
    view = CDSView(source=data_source, filters=[anime_js_filter])

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
        sizing_mode="stretch_width",
    )
    save(result)
    click.echo(f"Export anime plot to {output_filename}")


@plot_command_group.command(name="anime-trend")
@click.argument("db-uri")
@click.argument("output-filename", default="anime-trend.html")
def plot_anime_trend_command(db_uri: str, output_filename: str):
    """Plot the score and view count trand for new animes"""
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        score_stmt = (
            select(
                models.Anime.sn,
                models.Anime.name,
                models.AnimeScore.score,
                models.AnimeScore.insert_time,
            )
            .join(models.AnimeScore)
            .order_by(models.Anime.sn, models.AnimeScore.insert_time)
        )
        score_results = session.execute(score_stmt).fetchall()

        view_conut_stmt = (
            select(
                models.Anime.sn,
                models.Anime.name,
                models.AnimeViewCount.view_count,
                models.AnimeViewCount.insert_time,
            )
            .join(models.AnimeViewCount)
            .order_by(models.Anime.sn, models.AnimeViewCount.insert_time)
        )
        view_count_results = session.execute(view_conut_stmt).fetchall()

        stmt = (
            select(
                models.Anime.name,
                models.Anime.is_new,
                latest_view_count_cte.c.view_count,
                latest_score_cte.c.score,
            )
            .join(latest_view_count_cte)
            .join(latest_score_cte)
            .order_by(latest_view_count_cte.c.view_count.desc())
        )
        ani_results = session.execute(stmt)
        df = pd.DataFrame(ani_results.fetchall(), columns=ani_results.keys())
        column_sources = df.to_dict(orient="list")
        data_sources = ColumnDataSource(column_sources)

        stmt = select(sql_func.max(models.AnimeViewCount.view_count))
        max_view_count = session.execute(stmt).scalars().first()

    first_view_source, view_source_dict = _group_stat(view_count_results, "view_counts")

    anime_name_list = list(view_source_dict.keys())
    first_anime = anime_name_list[0]

    first_score_source, score_source_dict = _group_stat(
        score_results, "scores", first_anime
    )

    output_file(filename=output_filename, title="動畫瘋觀看、評分趨勢")

    view_pic = figure(x_axis_type="datetime")
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

    score_pic = figure(x_axis_type="datetime")
    score_pic.line("insert_times", "scores", source=first_score_source)
    score_pic.add_tools(
        HoverTool(
            tooltips=[
                ("score", "@scores{1.1}"),
                ("date: ", f"@insert_times{DATE_TIME_FORMAT}"),
            ],
            formatters={"@insert_times": "datetime"},
        )
    )

    ani_select = Select(title="作品", value=first_anime, options=anime_name_list)
    ani_select.js_on_change(
        "value",
        CustomJS(
            args={
                "view_counts_source_dict": view_source_dict,
                "view_source": first_view_source,
                "score_source_dict": score_source_dict,
                "score_source": first_score_source,
            },
            code=pkg_resources.resource_string(
                "bahamut_ani_stat.plot", "static/new-anime-source-update-dropdown.js"
            ).decode("utf-8"),
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
        code=pkg_resources.resource_string(
            "bahamut_ani_stat.plot", "static/dropdown-anime-filter.js"
        ).decode("utf-8"),
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
