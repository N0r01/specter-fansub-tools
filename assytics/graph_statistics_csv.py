import math,re,argparse,argcomplete,csv,sys
from collections import namedtuple
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator,FuncFormatter

def sec_to_mm_ss_str(sec):
    rs = round(sec, 2)
    s = '{0:02.0f}'.format(rs%60)
    return f"{int(rs / 60):02d}:{s}"

def str2s(hmrstr):
    mre = re.match("([0-9]+):([0-9]{2}):([0-9.]+)",hmrstr)
    h = int(mre[1])
    m = int(mre[2])
    s = float(mre[3])
    return ((h*60) + m ) * 60 + s

parser = argparse.ArgumentParser(description='graph data from libass_profiler_graph (assytics)')
parser.add_argument('-i', '--inputcsv',default='statistics.csv', required=False, help='name of the CSV file').completer = argcomplete.completers.FilesCompleter(['csv'], directories=False)
args = parser.parse_args()

frame_stat_names = ['time','total_image_size', 'largest_image_size','image_count','time_benchmark']
Frame_Statistics = namedtuple('Frame_Statistics', frame_stat_names)
frame_graph_labels = [
    'total bitmap sizes for frame',
    'largest bitmap size in frame',
    'bitmap counts',
    'frame render time',
]
frame_stat_y_axis_labels = [
    'bytes',
    'bytes',
    'counts',
    'seconds',
]

def Base10BytesFormatter(max_y):
    if max_y > 1000**3:
        return lambda y,pos: f"{'{:.1f}'.format(y/1000**3)} GB"
    elif max_y > 1000**2:
        return lambda y,pos: f"{'{:.1f}'.format(y/1000**2)} MB"
    elif max_y > 1000:
        return lambda y,pos: f"{'{:.1f}'.format(y/1000)} kB"
    else:
        return lambda y,pos: f"{int(y)}"

def graph_libass_stats(samples,title):
    zs = list(zip(*samples))
    time_domain = [str2s(t) for t in zs[0]]
    datasets = zs[1:]

    plt.style.use('dark_background')
    fig, subplots = plt.subplots(len(datasets), 1, constrained_layout=True)
    fig.suptitle(f'Analytics for {re.sub(".*/","",title)}')

    for subplot,dataset,graph_label,y_label in zip(subplots,datasets,frame_graph_labels,frame_stat_y_axis_labels):
        float_data = [float(a) for a in dataset]
        max_y = max(float_data)
        subplot.ticklabel_format(style='plain')
        subplot.xaxis.set_major_locator(MultipleLocator(60))
        subplot.xaxis.set_minor_locator(MultipleLocator(15))
        subplot.xaxis.set_major_formatter(FuncFormatter(lambda x,pos: sec_to_mm_ss_str(x)))
        subplot.grid(visible=True, which='major', axis='x', color='#333333')
        if y_label == "bytes":
            subplot.yaxis.set_major_formatter(Base10BytesFormatter(max_y))
        else:
            subplot.set(xlabel=None, ylabel=y_label)
        subplot.set_xlim([time_domain[0], time_domain[-1]])
        subplot.set_ylim([0, max_y])
        subplot.plot(time_domain,float_data)
        subplot.set_title(graph_label)
        plt.setp(subplot.get_xticklabels(), rotation=0, ha="left")
    plt.show()

data_list = []
with open(args.inputcsv, newline='') as csvfile:
    reader = csv.reader(csvfile)
    title = next(reader)[0]
    next(reader)
    for row in reader:
        print(row)
        data = Frame_Statistics(*row)
        data_list.append(data)
graph_libass_stats(data_list,title)
