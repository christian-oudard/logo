class GridIndex:

    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.index = {}

    def add(self, shape):
        for c in self.hash_shape(shape):
            self.index.setdefault(c, []).append(shape)

    def query(self, shape):
        for c in self.hash_shape(shape):
            yield from self.index.get(c, [])

    def hash_shape(self, shape):
        coords = [ self.hash(p) for p in shape ]
        x_lo = min(x for x, _ in coords)
        x_hi = max(x for x, _ in coords)
        y_lo = min(y for _, y in coords)
        y_hi = max(y for _, y in coords)
        all_coords = tuple(
            (x, y)
            for x in range(x_lo, x_hi+1)
            for y in range(y_lo, y_hi+1)
        )
        return all_coords

    def hash(self, p):
        x, y = p
        return (int(x // self.grid_size), int(y // self.grid_size))
