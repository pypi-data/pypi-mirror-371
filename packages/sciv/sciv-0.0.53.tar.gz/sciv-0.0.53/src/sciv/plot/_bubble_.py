# -*- coding: UTF-8 -*-

import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from pandas import DataFrame

from .. import util as ul
from ..util import path, plot_end

__name__: str = "plot_bubble"


def bubble(
    df: DataFrame,
    x: str,
    y: str,
    hue: str = None,
    size: str = None,
    width: float = 2,
    height: float = 2,
    title: str = None,
    output: path = None,
    show: bool = True
):
    if output is None and not show:
        ul.log(__name__).info(f"At least one of the `output` and `show` parameters is required")
    else:
        fig, ax = plt.subplots(figsize=(width, height))

        if title is not None:
            plt.title(title)

        if size is not None:
            _size_ = df[size].values
            sizes = (np.array(_size_).min(), np.array(_size_).max())
        else:
            sizes = None

        sns.relplot(
            x=x,
            y=y,
            hue=hue,
            size=size,
            sizes=sizes,
            alpha=.5,
            palette="muted",
            height=6,
            data=df
        )

        plot_end(fig, output, show)
