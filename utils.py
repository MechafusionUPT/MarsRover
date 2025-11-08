#utils
def clamp(x, lo=-1.0, hi=1.0):
    return max(lo, min(hi, float(x)))
