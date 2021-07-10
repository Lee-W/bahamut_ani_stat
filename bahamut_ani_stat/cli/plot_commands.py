import click
import pandas as pd
import sqlalchemy
from bokeh.io import output_file, save
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
