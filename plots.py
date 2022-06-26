import matplotlib.pyplot as plt

# 30 esperiments
number_of_rabbits = [24, 13, 0, 13, 33, 19, 33, 30, 18, 30, 7, 18, 7, 6, 16, 
30, 25, 70, 18, 49, 24, 54, 54, 34, 25, 24, 26, 33, 33, 7]
number_of_foxes = [313, 793, 787, 793, 841, 867, 841, 313, 304, 313, 855, 
867, 832, 811, 793, 313, 830, 348, 304, 360, 313, 328, 328, 841, 830, 313, 
833, 841, 841, 832]
1907      1898   

## combine these different collections into a list
data_to_plot = []
for i in range(30):
    data_to_plot.append((number_of_foxes[i]-number_of_rabbits[i]))

# Create a figure instance
fig, ax1 = plt.subplots()
val = ax1.violinplot(data_to_plot, showmeans=True, showextrema=True, showmedians=True)

plt.show()

"""Run 3: 2400, rabbit, eaten, 1
Run 5: 2400, rabbit, eaten, 1
Run 7: 2400, rabbit, eaten, 1
Run 15: 2400, rabbit, eaten, 1
Run 28: 2400, rabbit, eaten, 1
Run 29: 2400, rabbit, eaten, 1"""