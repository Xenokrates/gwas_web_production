from bokeh.io import output_file, show
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Row, Column, CustomJS, DataTable, TableColumn
from bokeh.io import curdoc

import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from pandas import DataFrame
from bokeh.models import ColumnDataSource, HoverTool, FixedTicker
import re

N = 50000


def sorted_chrs(l):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


def prepare_data(data1m):

    cut1 = data1m['pval'][data1m['pval'].argsort()[N]]

    data = np.ones(len(data1m), dtype=[('snp', np.dtype('U25')),
                                       ('pos', np.int),
                                       ('chr', np.dtype('U5')),
                                       ('pval1', float),
                                       ('pval1_q', float)])
    data['snp'] = data1m['snp']
    data['pos'] = data1m['pos']
    data['chr'] = data1m['chr']
    data['pval1'] = data1m['pval']

    data = data[(data['pval1'] < cut1)]

    for i in range(len(data)):
        data['pval1_q'][i] = 1.0 * np.sum(data['pval1'][i] >= data1m['pval']) / len(data1m)

    ts = DataFrame({'snp': data['snp'],
                    'pos': data['pos'],
                    'chr': data['chr'],
                    'color': np.zeros(len(data), dtype='S20'),
                    'abspos': data['pos'],
                    'pval1': -np.log10(data['pval1']),
                    'pval1_q': -np.log10(data['pval1_q'])})
    ts['gene'] = 'my gene'


    color_sequence = ['#7fc97f', "#beaed4", '#fdc086']
    upper_bound = np.ceil(np.max(ts['pval1']) + .51)

    chrs = np.unique(ts['chr'])
    if type(chrs[0]) == str:
        chrs = sorted_chrs(chrs)

    xtixks_pos = np.zeros(len(chrs) + 1)
    for i in range(len(chrs)):
        temp = ts['abspos'][ts['chr'] == chrs[i]]
        if len(temp) > 0:
            temp = np.max(temp)
        else:
            temp = 1000
        xtixks_pos[i + 1] = temp
    xtixks_pos = np.cumsum(xtixks_pos)
    for i in range(len(chrs)):
        ts['abspos'][ts['chr'] == chrs[i]] += xtixks_pos[i]
    xtixks_pos = (xtixks_pos[1:] + xtixks_pos[:-1]) / 2.0
    for i in range(len(chrs)):
        ts['color'][ts['chr'] == chrs[i]] = color_sequence[i % len(color_sequence)]


    #print (ts)
    source = ColumnDataSource(data=ts)
    print (source)
    return source, cut1, ts, upper_bound, xtixks_pos, chrs


def plot_qq(source):
    hoverq = HoverTool(
            tooltips=[
                ("chr", "@chr"),
                ("snp", "@snp"),
                ("pos", "@pos"),
                #("-log10(p-value)", "@pval1"),
                ("-log10(pval1,pval1_q)", "(@pval1, @pval1_q)"),
            ]
        )
    toolsq = ["tap","pan","box_zoom","wheel_zoom","save","reset", hoverq]
    pq1 = figure(title="Quantile-Quantile Plot",plot_width=900, plot_height=900, tools=toolsq)
    pq1.line([0, 7], [0, 7], line_width=3, color="black", alpha=0.5, line_dash=[4, 4])
    rq1 = pq1.circle('pval1_q', 'pval1', source=source, line_color=None, size=6)
    pq1.yaxis.axis_label = "Experimental quantiles, -log10(p)"
    pq1.xaxis.axis_label = "Theoretical quantiles, -log10(p)"
    return pq1


def plot_mahnhatten(source, cut1, ts, upper_bound, xtixks_pos, chrs):


    hover1 = HoverTool(
        tooltips=[
            ("chr", "@chr"),
            ("snp", "@snp"),
            ("pos", "@pos"),
            # ("-log10(pval1,pval2)", "(@pval1, @pval2)"),
            ("-log10(p-value)", "@pval1"),
        ]
    )
    tools1 = ["tap","pan","box_zoom","wheel_zoom","save","reset", hover1]

    p1 = figure(title="Manhatten Plot",
                plot_width=1500,
                plot_height=900,
                tools=tools1,
                x_range=[0, np.max(ts['abspos'])],
                y_range=[-0.12 * upper_bound, upper_bound])
    r1 = p1.circle('abspos', 'pval1', source=source, line_color=None, color='color', size=6)
    #r1.selection_glyph = selection_glyph
    #r1.nonselection_glyph = nonselection_glyph
    p1.patch([0, np.max(ts['abspos']), np.max(ts['abspos']), 0], [0, 0, -np.log10(cut1), -np.log10(cut1)], alpha=0.5,
             line_color=None, fill_color='gray', line_width=2)
    p1.yaxis.axis_label = "-log10(p)"
    p1.xaxis.axis_label = "Chromosomes"
    p1.xgrid.grid_line_color = None
    p1.xaxis[0].ticker = FixedTicker(ticks=[])

    p1.text(xtixks_pos, xtixks_pos * 0 - 0.12 * upper_bound, [str(chrs[i]) for i in range(len(chrs))],
            text_align='center')
    return p1


def get_table(source):
    columns = [
        TableColumn(field="chr", title="Chromosom"),
        TableColumn(field="snp", title="SNP"),
        TableColumn(field="pvalue", title="p-Value"),
        #TableColumn(field="pval1", title="-LOG10(p-Value)"),

       # TableColumn(field="gene", title="Gene Annotation")
    ]
    dt1 = DataTable(source=source, columns=columns, width=900, height=300)
    return dt1


def plot_both(plot1, plot2):
    output_file("test.html")

    show(row(plot1, plot2))


def start_plotting(gwas_file):
    dtypes = np.dtype([('snp', 'S10'),
                       ('chr', np.int32),
                       ('pos', np.int32),
                       ('pval', np.float64)])
    data1m = np.genfromtxt(gwas_file, dtype=dtypes,
                           usecols=(2, 3, 5, 6), delimiter=',', names=['snp', 'chr', 'pos', 'pval'], skip_header=1)



    source, cut1, ts, upper_bound, xtixks_pos, chrs = prepare_data(data1m)
    plot1 = plot_mahnhatten(source, cut1, ts, upper_bound, xtixks_pos, chrs)
    plot2 = plot_qq(source)
    dt1 = get_table(source)
    output_file("test.html")
    show(Column(Row(plot1, plot2), Row(dt1)))
    #plot_both(plot1, plot2)
