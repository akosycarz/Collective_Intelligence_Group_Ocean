import matplotlib.pyplot as plt

# Do plot of csv
# Do violin plot of end results

# 30 esperiments
number_of_rabbits = [24, 13, 0, 13, 33, 19, 33, 30, 18, 30, 7, 18, 7, 6, 16, 
30, 25, 70, 18, 49, 24, 54, 54, 34, 25, 24, 26, 33, 33, 7]
number_of_foxes = [313, 793, 787, 793, 841, 867, 841, 313, 304, 313, 855, 
867, 832, 811, 793, 313, 830, 348, 304, 360, 313, 328, 328, 841, 830, 313, 
833, 841, 841, 832]  

## combine these different collections into a list
data_to_plot = []
for i in range(30):
    data_to_plot.append((number_of_foxes[i]-number_of_rabbits[i]))

# Create a figure instance
fig, ax1 = plt.subplots()
val = ax1.violinplot(data_to_plot, showmeans=True, showextrema=True, showmedians=True)

plt.show()

# BASIC FRAME/NUMBER OF ANIMALS PLOT CODE 

rabbits = []
foxes = []
frames_rabbit = []
frames_fox = []
grass = []
frames_grass = []

df = open("competition_grass_15.csv", 'r').readlines()

for i in range(len(df)):
    line = df[i].split(',')
    if line[1] == 'rabbit' and line[2] == 'alive':
        rabbits.append(int(line[3]))
        frames_rabbit.append(int(line[0]))
    elif line[1] == 'fox' and line[2] == 'alive':
        foxes.append(int(line[3]))
        frames_fox.append(int(line[0]))
    elif line[1] == 'grass' and line[2] == 'alive' and int(line[0]) < 2500:
        grass.append(int(line[3]))
        frames_grass.append(int(line[0]))

# plot lines
plt.plot(frames_rabbit, rabbits, label = "rabbits")
plt.plot(frames_fox, foxes, label = "foxes")
plt.plot(frames_grass, grass, label = "grass")
plt.legend()
plt.xlabel('Frame')
plt.ylabel('Number of agents')
plt.savefig('juna.png')
