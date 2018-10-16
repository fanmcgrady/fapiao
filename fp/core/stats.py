def online_mean(x_mean, new_x, n):
    return (x_mean * n + new_x) / (n + 1.)


def online_var(x_mean, x_var, new_x, n):
    return (x_var * n + (new_x - x_mean) ** 2) / (n + 1.)


def online_std(x_mean, x_std, new_x, n):
    return (x_std * n + abs(new_x - x_mean)) / (n + 1.)
