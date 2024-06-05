import numpy as np

class GenomeScalar:
    genes: np.ndarray

    def __init__(self, genes: np.ndarray):
        self.genes = genes

    def combineWith(self, other):
        return GenomeScalar(self.genes + other.genes) / 2

    def __add__(self, other):
        self.genes += other
        return self

    def __sub__(self, other):
        self.genes -= other
        return self

    def __mul__(self, other):
        self.genes *= other
        return self

    def __truediv__(self, other):
        self.genes /= other
        return self

    def __floordiv__(self, other):
        self.genes //= other
        return self

    def __mod__(self, other):
        self.genes %= other
        return self

    def __pow__(self, other):
        self.genes **= other
        return self

    def __eq__(self, other):
        return self.genes == other

    def __ne__(self, other):
        return self.genes != other

    def __lt__(self, other):
        return self.genes < other

    def __le__(self, other):
        return self.genes <= other

    def __gt__(self, other):
        return self.genes > other

    def __ge__(self, other):
        return self.genes >= other

    def __str__(self):
        return str(self.genes)
    
    def __repr__(self):
        return f"GenomeScalar({self.genes})"