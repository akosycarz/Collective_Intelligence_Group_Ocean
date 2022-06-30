import matplotlib.pyplot as plt
import numpy as np

# VIOLIN PLOT OF LAST VALUESs

# 30 esperiments
"""number_of_rabbits_basic = [1005, 1042, 1070, 1015, 1015, 1024, 1011, 1053, 
1032, 1021, 1015, 1029, 1038, 1045, 1032, 1035, 1023, 1034, 1071, 1005, 
1048, 1033, 1017, 1020, 1021, 1058, 1026, 1051, 1033, 1061]
number_of_rabbits_grass = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
number_of_rabbits_repr = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 
1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 
1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
number_of_rabbits_all = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
number_of_foxes_basic = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
number_of_foxes_grass = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
number_of_foxes_repr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
number_of_foxes_all = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

## combine these different collections into a list
data_to_plot = [number_of_rabbits_basic, number_of_foxes_basic, 
number_of_rabbits_grass, number_of_foxes_grass, number_of_rabbits_repr, 
number_of_foxes_repr, number_of_rabbits_all, number_of_foxes_all]
# Create a figure instance
fig, ax1 = plt.subplots()
val = ax1.violinplot(data_to_plot, showmeans=True, showextrema=True, showmedians=True)

ax1.set_xlabel("Experiment",size = 16,alpha=0.7)
ax1.set_ylabel("Number of agents",size = 16,alpha=0.7)
plt.legend(["rabbit", "fox"], loc='upper right')
plt.savefig('pupu3.png')"""

# BASIC FRAME/NUMBER OF ANIMALS PLOT CODE 

for i in range(30):
    rabbits = []
    foxes = []
    frames_rabbit = []
    frames_fox = []
    grass = []
    frames_grass = []

    filename = "competition_{}.csv".format(i)
    df = open(filename, 'r').readlines()

    for i in range(len(df)):
        line = df[i].split(',')
        if line[1] == 'rabbit' and line[2] == 'alive':
            rabbits.append(int(line[-1]))
            frames_rabbit.append(int(line[0]))
        elif line[1] == 'fox' and line[2] == 'alive':
            foxes.append(int(line[-1]))
            frames_fox.append(int(line[0]))
        elif line[1] == 'grass' and line[2] == 'alive' and int(line[0]) < 2500:
            grass.append(int(line[-1]))
            frames_grass.append(int(line[0]))

    # plot lines
    plt.plot(frames_rabbit, rabbits, color='blue')
    plt.plot(frames_fox, foxes, color='red')
    plt.plot(frames_grass, grass, color='green')
plt.legend(["rabbits", "foxes", "grass"])
plt.xlabel('Frame')
plt.ylabel('Number of agents')
plt.savefig('line_all.png')


def set_axis_style(ax, labels):
    ax.xaxis.set_tick_params(direction='out')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks(np.arange(1, len(labels) + 1), labels=labels)
    ax.set_xlim(0.25, len(labels) + 0.75)
    ax.set_xlabel('Sample name')

# VIOLIN PLOT CODE FOR ALL/ONE SIMULATIONS:
"""data_to_plot = []

for i in range(15,16):
    rabbits = []
    foxes = []
    frames = []

    filename = "competition_sexual_reproduction_{}.csv".format(i)
    df = open(filename, 'r').readlines()

    for i in range(len(df)):
        line = df[i].split(',')
        if line[1] == 'rabbit' and line[2] == 'alive':
            rabbits.append(int(line[-1]))
            frames.append(int(line[0]))
            foxes.append(0)
        elif line[1] == 'fox' and line[2] == 'alive':
            foxes.append(int(line[-1]))
            frames.append(int(line[0]))
            rabbits.append(0)

    data_to_plot.append(rabbits)
    data_to_plot.append(foxes)
    
fig, ax1 = plt.subplots()
val = ax1.violinplot(data_to_plot, showmeans=True, showextrema=True, showmedians=True)
for j in range(len(val['bodies'])):
    if j % 2 == 0:
        val['bodies'][j].set_facecolor('blue')
        val['bodies'][j].set_edgecolor('darkblue')
    else:
        val['bodies'][j].set_facecolor('red')
        val['bodies'][j].set_edgecolor('darkred')

# set style for the axes
labels = ['rabbit', 'fox']
#'1', '', '2', '', '3', '', '4', '', '5', '', '6', '', '7', '', 
#'8', '', '9', '', '10', '', '11', '', '12', '', '13', '', '14', '', '15', 
#'', '16', '', '17', '', '18', '', '19', '', '20', '', '21', '', '22', '', 
#'23', '', '24', '', '25', '', '26', '', '27', '', '28', '', '29', '', '30', '']
set_axis_style(ax1, labels)

ax1.set_xlabel("Simulation 15",size = 16,alpha=0.7)
ax1.set_ylabel("Number of agents",size = 16,alpha=0.7)
plt.legend(["rabbit", "fox"], loc='upper left')
plt.savefig('violin2.png')"""


# VIOLIN PLOT CODE FOR ALL MODELS & ONE SIMULATION:
"""data_to_plot = []

for i in ["competition_basic_15.csv", "competition_grass_15.csv", "competition_sexual_reproduction_15.csv", "competition_15.csv"]:
    print(i)
    rabbits = []
    foxes = []
    frames = []

    df = open(i, 'r').readlines()

    for i in range(len(df)):
        line = df[i].split(',')
        if line[1] == 'rabbit' and line[2] == 'alive':
            rabbits.append(int(line[-1]))
            frames.append(int(line[0]))
            foxes.append(0)
        elif line[1] == 'fox' and line[2] == 'alive':
            foxes.append(int(line[-1]))
            frames.append(int(line[0]))
            rabbits.append(0)

    data_to_plot.append(rabbits)
    data_to_plot.append(foxes)
    
fig, ax1 = plt.subplots()
val = ax1.violinplot(data_to_plot, showmeans=True, showextrema=True, showmedians=True)
for j in range(len(val['bodies'])):
    if j % 2 == 0:
        val['bodies'][j].set_facecolor('blue')
    else:
        val['bodies'][j].set_edgecolor('red')

ax1.set_xlabel("Simulation 15",size = 16,alpha=0.7)
ax1.set_ylabel("Number of agents",size = 16,alpha=0.7)
plt.legend(["rabbit", "fox"], loc='upper left')
plt.savefig('pupu4.png')"""

