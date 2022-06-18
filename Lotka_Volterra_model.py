import matplotlib.pyplot as plt


# model parameters
a = 0.7; b = 0.5; c = 0.3;  e = 0.2
dt = 0.001; max_time = 100

# initial time and populations
# u = rabbits
# v = foxes
# t = time
t = 0; u = 1.0; v = 0.5

# empty lists in which to store time and populations
t_list = []; u_list = []; v_list = []

# initialize lists
t_list.append(t); u_list.append(u); v_list.append(v)

while t < max_time:
    # calc new values for t, u, v
    t = t + dt
    u = u + (a * u - b * u * v) * dt
    v = v + (-c * v + e * u * v) * dt

    # store new values in lists
    t_list.append(t)
    u_list.append(u)
    v_list.append(v)

# Plot the results
plot = plt.plot(t_list, u_list, 'b', t_list, v_list, 'g', linewidth = 2)
plt.show()