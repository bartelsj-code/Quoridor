import numpy as np

def init_union_find(n):
    parent = np.arange(n, dtype=np.int8)
    rank = np.zeros(n, dtype=np.int8)
    return parent, rank

def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]

def union(parent, rank, x, y):
    root_x = find(parent, x)
    root_y = find(parent, y)

    if root_x == root_y:
        return
    
    if rank[root_x] > rank[root_y]:
        parent[root_y] = root_x
    elif rank[root_x] < rank[root_y]:
        parent[root_x] = root_y
    else:
        parent[root_y] = root_x
        rank[root_x] +=np.uint8(1)

def grid_index(row, col):
    return row * 9 + col


def display_uf(parent, rank):
    print("parent:", parent)
    print("rank:", rank)
    


