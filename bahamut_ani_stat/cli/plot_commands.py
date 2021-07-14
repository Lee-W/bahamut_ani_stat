import click
import pandas as pd
import sqlalchemy
from bokeh.io import output_file, save
from bokeh.models import ColumnDataSource, DataTable, DateFormatter, TableColumn
from bokeh.plotting import figure
from sqlalchemy import select
from sqlalchemy.orm import Session

from bahamut_ani_stat.db import models


@click.group(name="plot")
def plot_command_group():
    pass


@plot_command_group.command(name="premium-rate")
@click.argument("db-uri")
@click.argument("output-filename", default="premium-rate.html")
def plot_premium_rate_command(db_uri: str, output_filename: str):
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = select(models.PremiumRate)
        results = session.execute(stmt).scalars().all()

        data = {row.insert_time: row.premium_rate for row in results}

    pr_series = pd.Series(data)
    pr_series.index = pr_series.index.date
    idx = pd.date_range(pr_series.index.min(), pr_series.index.max())
    pr_series = pr_series.reindex(idx)
    pr_series = pr_series.interpolate(method="pad")

    output_file(filename=output_filename, title="巴哈姆特動畫瘋 - 付費比例")
    p = figure(
        title="巴哈姆特動畫瘋 - 付費比例",
        x_axis_label="記錄時間",
        y_axis_label="付費比例",
        x_axis_type="datetime",
    )
    p.line(pr_series.index, pr_series.values)
    save(p)
    click.echo(f"Export premium plot to {output_filename}")


@plot_command_group.command(name="anime")
@click.argument("db-uri")
@click.argument("output-filename", default="anime.html")
def plot_anime_command(db_uri: str, output_filename: str):
    engine = sqlalchemy.create_engine(db_uri)
    with Session(engine) as session, session.begin():
        stmt = select(models.PremiumRate)
        results = session.execute(stmt).scalars().all()

        stmt = select(models.Anime)
        results = session.execute(stmt).scalars().all()
        column_sources = {
            "sn": [row.sn for row in results],
            "name": [row.name for row in results],
            "release_time": [row.release_time for row in results],
            "upload_hour": [row.upload_hour for row in results],
            "is_new": [row.is_new for row in results],
            "anime_view_counts": [
                row.anime_view_counts[-1].view_count if row.anime_view_counts else -1
                for row in results
            ],
            "anime_scores": [
                row.anime_scores[-1].score if row.anime_scores else -1
                for row in results
            ],
        }

    source = ColumnDataSource(column_sources)

    output_file(filename=output_filename, title="巴哈姆特動畫瘋 - 所有動畫")
    columns = [
        TableColumn(field="sn", title="sn"),
        TableColumn(field="name", title="動畫名稱"),
        TableColumn(field="is_new", title="是否為新番"),
        TableColumn(field="anime_view_counts", title="觀看人次"),
        TableColumn(field="anime_scores", title="評分"),
        TableColumn(field="release_time", title="動畫釋出時間", formatter=DateFormatter()),
        TableColumn(field="upload_hour", title="動畫每週上架時間（新番）"),
    ]
    data_table = DataTable(
        source=source, columns=columns, height_policy="max", width_policy="max"
    )
    save(data_table)
    click.echo(f"Export anime plot to {output_filename}")
