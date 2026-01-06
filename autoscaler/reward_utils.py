def reward_function(lat, replicas, low_t, high_t):
    r = 0.0
    if lat < low_t:
        r += 5
    elif lat < high_t:
        r += 2
    else:
        r -= 5
    r -= (replicas - 1) * 1.0
    return r
