

def diff(t_k, x_t): # Parameters must be 2 arrays of equal length
    if len(t_k) != len(x_t):
        print("ERROR: time value array doesn't match signal value array x")
        return
    
    # Return the coputed discrete derivative v_t as a python array
    v_t = [None] * (len(t_k))
    v_t[0] = 0 # assume first element 0
    for i in range(1, len(t_k)): # Here k must start at 1 (index)
        v_t[i] = (x_t[i] - x_t[i-1])/(t_k[i]-t_k[i-1])
    
    print(v_t)
    return v_t


