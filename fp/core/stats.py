

def online_mean(mean_x, new_x, n):
    return (mean_x * n + new_x) / (n + 1.)

def online_var(mean_x, var_x, new_x, n):
    return (var_x * n + (new_x - mean_x)**2) / (n + 1.)