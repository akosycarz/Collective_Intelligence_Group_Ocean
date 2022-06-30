# number of animals per death cause (animal kind, average per model)

starved_rabbit = 0
starved_fox = 0
killed_rabbit = 0

for i in range(30):
    filename = "competition_{}.csv".format(i)
    df = open(filename, 'r').readlines()

    for i in range(len(df)):
        line = df[i].split(',')
        if line[1] == 'rabbit' and line[2] == 'starvation':
            starved_rabbit += 1
        elif line[1] == 'rabbit' and line[2] == 'eaten':
            killed_rabbit += 1
        elif line[1] == 'fox' and line[2] == 'starved':
            starved_fox += 1

print(starved_rabbit/30, starved_fox/30, killed_rabbit/30)
