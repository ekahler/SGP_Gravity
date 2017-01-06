# Plot_A10.py
#
# Takes output file from Parse_A10 (.txt) and generates time-series plots.
#
# Plots are not automatically saved. They can be saved by using the save
# button in the figure window, or by
#
# plt.savefig('\path\to\savefile.svg')
#
# SVG format imports correctly into Illustrator. If using a different format,
# one might need to change the line at the end ('plt.rcParams(...)') to a
# different file type.
#
# NB: Error bars are fixed at +/-10 uGal
#
# Jeff Kennedy, USGS

import numpy as np
from numpy import mod
import pylab as plt
from dateutil import parser
import datetime
import tkFileDialog
import matplotlib.dates as mdates
import matplotlib.ticker as tkr
import requests

def get_nwis_data(cross_ref_file, site_ID):
    with open(cross_ref_file, 'r') as fid:
        for line in fid:
            discrete_x, discrete_y = [], []
            continuous_x, continuous_y = [], []
            out_dic = dict()
            grav_ID, nwis_ID = line.strip().split(',')
            if grav_ID == site_ID:
                nwis_URL = 'http://nwis.waterdata.usgs.gov/nwis/dv?cb_72019=on&format=rdb_meas' + \
                           '&site_no=%s' + \
                           '&referred_module=gw&period=&begin_date=2008-10-17&end_date=2016-10-16'
                r = requests.get(nwis_URL % nwis_ID)
                nwis_data = r.text.split('\n')
                for line in nwis_data:
                    line_elems = line.split('\t')
                    if line_elems[0] == u'USGS':
                        if line_elems[3] != u'':
                            discrete_x.append(parser.parse(line_elems[2]))
                            discrete_y.append(float(line_elems[6]))
                        elif line_elems[4] != u'':
                            continuous_x.append(parser.parse(line_elems[2]))
                            continuous_y.append(float(line_elems[4]))
                out_dic['continuous_x'] = continuous_x
                out_dic['continuous_y'] = continuous_y
                out_dic['discrete_x'] = discrete_x
                out_dic['discrete_y'] = discrete_y
                return out_dic

        else:
            return 0

# Formats y-axis labels
def func(x, pos):
    s = '{:0,d}'.format(int(x))
    return s

# def to_float(d, epoch=arr1[0]):
#     return (d - epoch).total_seconds()

# Value to subtract from observed gravity so the plotted values are reasonable
offset = 978990000

# Open dialog to specify input file. Alternatively, specify file directly.
#Tkinter.Tk().withdraw() # Close the root window
cross_ref_file = 'SiteIDcrossref.csv'



# fig, ax1 = plt.subplots()
# ax1.plot(discrete_x, discrete_y, 'g.')
# ax1.plot(continuous_x, continuous_y, 'b-')
# ax1.invert_yaxis()
# plt.show()

data_file = tkFileDialog.askopenfilename(title="Select text file to plot (from A10_parse.py)")
# data_file = "SanPedro_qaqc.txt"

plt.ion()
stations = []
myFmt = mdates.DateFormatter('%Y')
y_format = tkr.FuncFormatter(func)

# Get station list and column numbers
with open(data_file) as fp:
    a = fp.readline()
    tags = a.split("\t")
    date_col = tags.index("Date")
    sta_col = tags.index("Station Name")
    grav_col = tags.index("Gravity")
    for line in fp:
        a = line.split("\t")
        stations.append(a[sta_col])
stations = list(set(stations))

# Initialize blank array to hold data. First array of each list element is date, second is gravity.
data = [[[],[]]]
nwis_data = ['']*len(stations)
for i in range(len(stations)-1):
    data.append([[],[]])

for station in stations:
    sta_index = stations.index(station)
    nwis_data[sta_index] = (get_nwis_data(cross_ref_file, station))
    if nwis_data[sta_index] != 0:
        nwis_data[sta_index]['station'] = station
# Get data from input file
with open(data_file) as fp:
    a = fp.readline()
    for line in fp:
        a = line.split("\t")
        sta = a[sta_col]
        print sta
        sta_index = stations.index(sta)
        # using the dateutil parser we can plot dates directly
        data[sta_index][0].append(parser.parse(a[date_col]))
        data[sta_index][1].append(float(a[grav_col])-offset)

threshold = datetime.timedelta(days=5)
for idx, sta in enumerate(nwis_data):
    if sta != 0:
        if sta['continuous_x'] != [] and sta['discrete_x'] != []:
            plot_x, plot_y = [], []
            min_delta_cont, min_delta_disc = datetime.timedelta(days=1000000), datetime.timedelta(days=1000000)
            for g_idx, g_date in enumerate(data[idx][0]):
                if sta['continuous_x'] != []:  # find closest continuous data
                    repdate = np.repeat(g_date, len(sta['continuous_x']))
                    delta_cont = np.asarray(sta['continuous_x']) - repdate
                    min_delta_cont = min(np.absolute(delta_cont))
                    idx_cont = np.where(delta_cont == min_delta_cont)[0]
                    if len(idx_cont) == 0:
                        idx_cont = len(delta_cont) - 1  # if all of delta_cont is < g meas., idx_cont is empty. this fixes.
                if sta['discrete_x'] != []:  # and closest discrete data
                    repdate = np.repeat(g_date, len(sta['discrete_x']))
                    delta_disc = np.asarray(sta['discrete_x']) - repdate
                    min_delta_disc = min(np.absolute(delta_disc))
                    idx_disc = np.where(delta_disc == min_delta_disc)[0]
                    if len(idx_disc) == 0:
                        idx_disc = len(delta_disc) - 1
                if min_delta_cont < threshold or min_delta_disc < threshold:
                    if min_delta_cont < min_delta_disc:
                        plot_x.append(sta['continuous_y'][idx_cont])
                        plot_y.append(data[idx][1][g_idx])
                    elif min_delta_cont > min_delta_disc:
                        plot_x.append(sta['discrete_y'][idx_disc])
                        plot_y.append(data[idx][1][g_idx])
                    else:
                        out_data = []
                else: # No water-level measurements are very close. Check if we can interpolate.
                    cont_gap, disc_gap = datetime.timedelta(days=1000000), datetime.timedelta(days=1000000)
                    if sta['continuous_x'] != []:  # calculate continuous gap
                        if any(i < 0 for i in delta_cont) and any(i > 0 for i in delta_cont): # Check if data on both sides of gap
                            closest_neg = max([i < 0 for i in delta_cont]) # time delta to closest negative diff
                            closest_pos = min([i > 0 for i in delta_cont])
                            idx_closest_neg_cont = np.where(delta_cont == closest_neg)
                            idx_closest_pos_cont = np.where(delta_cont == closest_pos)
                            cont_gap = np.absolute(closest_neg) + closest_pos

                    if sta['discrete_x'] != []:
                        if any(i < 0 for i in delta_disc) and any(i > 0 for i in delta_disc):  # Check if data on both sides of gap
                            closest_neg = max([i < 0 for i in delta_disc]) # time delta to closest negative diff
                            closest_pos = min([i > 0 for i in delta_disc])
                            idx_closest_neg_disc = np.where(delta_disc == closest_neg)
                            idx_closest_pos_disc = np.where(delta_disc == closest_pos)
                            disc_gap = np.absolute(closest_neg) + closest_pos
                    if cont_gap < disc_gap: # interpolate the data type with the smaller gap
                        x1 = sta['continuous_x'][idx_closest_neg_cont]
                        x2 = sta['continuous_x'][idx_closest_pos_cont]
                        y1 = sta['continuous_y'][idx_closest_neg_cont]
                        y2 = sta['continuous_y'][idx_closest_pos_cont]
                    elif disc_gap < cont_gap:
                        x1 = sta['discrete_x'][idx_closest_neg_cont]
                        x2 = sta['discrete_x'][idx_closest_pos_cont]
                        x1 = sta['discrete_y'][idx_closest_neg_cont]
                        x2 = sta['discrete_y'][idx_closest_pos_cont]
                    else:
                        print "no valid data to interpolate"
            plot_y = [(y-min(plot_y))/12.77 for y in plot_y]
            poly = np.polyfit(plot_x, plot_y, 1)
            cc = np.corrcoef(plot_x, plot_y)[0,1]
            line_x = np.linspace(min(plot_x)-0.2, max(plot_x)+0.2,10)
            p = np.poly1d(poly)
            line_y = p(line_x)
            plt.figure()
            plt.plot(plot_x, plot_y,'.')
            plt.plot(line_x,line_y)
            plt.title(sta['station'])
            ax = plt.gca()
            plt.ylabel('Inches of free-standing water,\n from gravity data')
            plt.xlabel('Depth to water, ft')
            plt.figtext(0.1, 0.25, 'Sy = %0.2f' % np.absolute(poly[0]))
            plt.figtext(0.1, 0.21, 'r^2 = %0.2f' % cc*-1)
            plt.show()
#         ts = np.linspace(sta.min(),sta.max(),1000)
#         plt.errorbar(data[figidx+ii][0],data[figidx+ii][1],yerr=10,fmt='kd')
#         ax = plt.gca()
#         ax2 = ax.twinx()
#         if nwis_data[figidx+ii] != 0:
#             ax2.plot(nwis_data[figidx+ii]['continuous_x'], nwis_data[figidx+ii]['continuous_y'])
#             ax2.invert_yaxis()
# # Remove scientific notation from axes labels
#         ax.yaxis.get_major_formatter().set_useOffset(False)
# # Add commas to y-axis tick mark labels
#         ax.yaxis.set_major_formatter(y_format)
# # Set x-axis tick labels to just show year
#         ax.xaxis.set_major_formatter(myFmt)
#
# # Adjust ticks so they fall on Jan 1 and extend past the range of the data. If there
# # are data in January and December, add another year so that there is plenty of space.
#         start_month = data[figidx+ii][0][0].month
#         start_year = data[figidx+ii][0][0].year
#         end_month = data[figidx+ii][0][-1].month
#         end_year = data[figidx+ii][0][-1].year
#         if start_month == 1:
#             start_year = start_year-1
#         if end_month == 12:
#             end_year = end_year + 1
#         xticks = []
#         for iii in range(start_year,end_year+2):
#             xticks.append(datetime.datetime(iii,1,1))
#         ax.set_xticks(xticks)
#         plt.title(stations[figidx+ii])
#         plt.draw()
#
#         plt.subplots_adjust(bottom=0.25, hspace=0.4, left=0.25, right=0.85)
# # When saved, this exports fonts as fonts instead of paths:
#         plt.rcParams['svg.fonttype'] = 'none'
# This keeps the figure windows open until the user closes them:
raw_input()


