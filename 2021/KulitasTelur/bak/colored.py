def get(arr):
    colored = []
    # rows
    for i in arr:
        # cols
        cols = []
        for j in i:
            if j[0] > 0 and j[1] > 0 and j[2] > 0:
                cols.append(j)
        colored.append(cols)
    return colored

