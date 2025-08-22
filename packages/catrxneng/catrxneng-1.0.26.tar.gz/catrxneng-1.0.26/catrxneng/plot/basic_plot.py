import plotly.graph_objects as go, numpy as np
from catrxneng.utils import plot_info_box


class BasicPlot:

    def __init__(self, title=None):
        self.fig = go.Figure()
        self.title = title
        self.right_axis = False

    def add_trace(self, x, y, name=None, mode="lines", yaxis="y1", hover_label=None):
        if isinstance(y, (float, int)):
            if x is not None:
                xmin = np.min(x)
                xmax = np.max(x)
            x = [xmin, xmax]
            y = [y, y]
        trace = go.Scatter(
            x=x,
            y=y,
            mode=mode,
            yaxis=yaxis,
            name=name,
            text=hover_label,
            hovertemplate="<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>",
        )
        self.fig.add_trace(trace)

    def render(
        self,
        xlabel,
        ylabel,
        xrange=None,
        yrange=None,
        ylabel2=None,
        yrange2=None,
        info_text=None,
    ):
        if xrange is None:
            xrange = [None, None]
        if yrange is None:
            yrange = [None, None]
        if yrange2 is None:
            yrange2 = [None, None]

        top = 50
        width = 700
        if info_text is None:
            bottom = 50
            height = 400
        else:
            bottom = 110
            height = None

        yaxis2 = None
        if ylabel2:
            yaxis2 = dict(
                title=f"<b>{ylabel2}</b>",
                range=yrange2,
                showline=True,
                linecolor="black",
                linewidth=2,
                mirror=True,
                nticks=9,
                overlaying="y",
                side="right",
            )
        self.fig.update_layout(
            title=dict(text=f"<b>{self.title}</b>", x=0.5),
            xaxis_title=f"<b>{xlabel}</b>",
            yaxis_title=f"<b>{ylabel}</b>",
            width=width,
            height=height,
            margin=dict(t=top, b=bottom),
            yaxis=dict(
                range=yrange,
                showline=True,
                linecolor="black",
                linewidth=2,
                mirror=True,
                nticks=9,
            ),
            yaxis2=yaxis2,
            xaxis=dict(
                range=xrange,
                showline=True,
                linecolor="black",
                linewidth=2,
                mirror=True,
            ),
            legend=dict(
                x=1.05,
                y=1,
                xanchor="left",
                yanchor="top"
            ),
            annotations=plot_info_box(info_text),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        self.fig.show()
