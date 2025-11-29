class Matrix():
    def __init__(self, matrix = None, rows = None, columns = None,identity = False):
        if matrix is not None:
            if identity:
                raise ValueError("Identity=True conflicts with matrix argument")
            if not matrix or not matrix[0]:
                raise ValueError("Matrix must be non-empty")
            
            rows = len(matrix)
            columns = len(matrix[0])

            if any(len(row) != columns for row in matrix):
                raise ValueError("All rows must have the same length")
            
            self.matrix = matrix
        else:
            if rows is None or columns is None:
                raise ValueError("Must provide both arguments (rows, columns) when matrix is None ")
            if rows<0 or columns<0:
                raise ValueError("Arguments (rows,columns) must be positive")
            if identity:
                if rows != columns:
                    raise ValueError("Identity matrix must be square")
                self.matrix = [[1 if i==j else 0 for j in range(columns)] for i in range(rows)]
            else:
                self.matrix = [[0 for _ in range(columns)] for _ in range(rows)]
        
        self.rows = rows
        self.columns = columns
        self.isSquare = self.isSquare()
        self.isBinary = self.isBinary()

    def _update_flags(self):
        self.isSquare = self.isSquare()
        self.isBinary = self.isBinary()

    def isSquare(self):
        return (self.rows == self.columns)

    def isBinary(self):
        return all(x in (0,1) for row in self.matrix for x in row)
    
    def transpose(self):
        t = Matrix(rows=self.columns, columns=self.rows)
        
        for i in range(self.rows):
            for j in range(self.columns):
                t.matrix[j][i] = self.matrix[i][j]
        return t
    
    def multiplication(self, multiplier):
        if self.columns != multiplier.rows:
            raise ValueError("Shape mismatch on multiplication")
        
        product = Matrix(rows=self.rows, columns=multiplier.columns)
        multT = multiplier.transpose()
        
        for i in range(product.rows):
            for j in range(product.columns):
                for k in range(self.columns):
                    product.matrix[i][j]+= self.matrix[i][k] * multT.matrix[j][k]
        
        return product
    
    def dotMultiplication(self, scalar):
        product = Matrix(rows=self.rows, columns=self.columns)

        for i in range(product.rows):
            for j in range(product.columns):
                product.matrix[i][j] = self.matrix[i][j] * scalar

        return product
    
    def power(self, pow):
        if not self.isSquare:
            raise ValueError("power() requires a square matrix")
        base = self
        result = Matrix(rows=self.rows, columns=self.columns, identity=True)
        for _ in range(pow):
            result = result.multiplication(base)
        return result
    
    def boolean_multiplication(self, multiplier):
        if self.columns != multiplier.rows:
            raise ValueError(f"Shape mismatch on boolean multiplication")

        product = Matrix(rows=self.rows, columns=multiplier.columns)
        multT = multiplier.transpose()

        for i in range(product.rows):
            for j in range(product.columns):
                val = 0
                for k in range(self.columns):
                    # AND then OR; coerce to bool in case entries aren't 0/1
                    if (self.matrix[i][k] != 0) and (multT.matrix[j][k] != 0):
                        val = 1
                        break  # early exit once we know there's at least one path
                product.matrix[i][j] = val
        return product

    def boolean_power(self, n):
        if self.rows != self.columns:
            raise ValueError("boolean_power requires a square matrix")
        if n == 0:
            # reachability in 0 steps: identity (self-loops only)
            I = Matrix(rows=self.rows, columns=self.columns, identity=True)
            return I
        result = Matrix(matrix=[row[:] for row in self.matrix])  # copy of A
        for _ in range(n-1):
            result = result.boolean_multiplication(self)
        return result
    
    def __str__(self):
        lines = []
        for i in range(self.rows):
            row = "".join("%-3d " % self.matrix[i][j] for j in range(self.columns)).rstrip()
            lines.append(row)
        return "\n".join(lines)
    
    def printAttributes(self):
        print(f"Rows      : {self.rows}")
        print(f"Columns   : {self.rows}")
        print(f"Is Square : {self.isSquare}")
        print(f"Is Binary : {self.isBinary}")

# I
matrixI = Matrix([
    [0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0],
    [0, 1, 0, 1, 1, 1],
    [0, 1, 1, 0, 1, 0],
    [0, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0]
])

#II
matrixII = Matrix([
    [0, 1, 1, 0, 0],
    [1, 0, 0, 1, 1],
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0]
])
#VIII
matrixVIII = Matrix([
    [0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 1, 0, 1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 1, 0, 0, 1, 0, 1, 1],
    [0, 0, 0, 1, 0, 0 ,0 ,1 ,0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
])
#A
matrixA = Matrix([
    [0, 1, 1, 0],
    [1, 0, 1, 0],
    [1, 1, 0, 1],
    [0, 0, 1, 0]
])
#B
matrixB = Matrix([
    [0, 1, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 1],
    [0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 1],
    [0, 1, 1, 1, 1, 0]
])


print("\nMatrix I\n")
for n in range(4):
    print(f"\n{n} {"steps" if n!=1 else "step"}\n")
    print(matrixI.boolean_power(n))

print("\nMatrix II\n")
for n in range(4):
    print(f"\n{n} {"steps" if n!=1 else "step"}\n")
    print(matrixII.boolean_power(n))

print("\nMatrix VII\n")
for n in range(4):
    print(f"\n{n} {"steps" if n!=1 else "step"}\n")
    print(matrixVIII.boolean_power(n))

print("\nMatrix A\n")
for n in range(5):
    print(f"\n{n} {"steps" if n!=1 else "step"}\n")
    print(matrixA.boolean_power(n))

print("\nMatrix B\n")
for n in range(5):
    print(f"\n{n} {"steps" if n!=1 else "step"}\n")
    print(matrixB.boolean_power(n))
