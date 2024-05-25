import numpy as np
from scipy.integrate import quad

λ = 1

def p(x):
    return 1

def q(x):
    return λ

def f(x):
    return -2 * λ * np.sin(np.sqrt(λ) * x)

def phi_j(j):
    h = x[1] - x[0]

    def function(xj): 
        if j == 0:
            if ((x[0] <= xj) and (xj <= x[1])):
                return (x[1] - xj) / h
            else:
                return 0
        elif j == N:
            if ((x[N] <= xj) and (x[N-1] >= xj)):
                return (xj - x[N-1]) / h
            else:
                return 0
        else:
            if (x[j-1] <= xj) and (x[j] >= xj):
                return (xj - x[j-1]) / h
            elif (x[j] <= xj) and (x[j+1] >= xj):
                return (x[j+1] - xj) / h
            else:
                return 0
    return function

N = 1000
a = 0  
b = np.pi  
x = np.linspace(a, b, N+1)
h = np.diff(x)

A = np.zeros((N-1, N-1))
rhs = np.zeros(N-1)

for j in range(1, N):

    # coeffs
    bj = quad(lambda z: (-p(z) + q(z) * (z - x[j-1]) * (x[j] - z)), x[j-1], x[j])[0] / (h[j-1] ** 2)
    bj1 = quad(lambda z: (-p(z) + q(z) * (z - x[j]) * (x[j+1] - z)), x[j], x[j+1])[0] / (h[j] ** 2)


    # simplify array indexing
    i = j - 1

    if j > 1:
        A[i, i-1] = bj
    if j < N-1:
        A[i, i+1] = bj1

    # todo: redo
    diag1 = lambda z: p(z) + q(z) * (z - x[j-1])**2
    diag2 = lambda z: p(z) + q(z) * (x[j+1] - z)**2
    A[i, i] = (quad(diag1, x[j-1], x[j])[0] + quad(diag2, x[j], x[j+1])[0]) / (h[j-1] ** 2)

    rhs[i] = (quad(lambda z: (z - x[j-1]) * f(z), x[j-1], x[j])[0] + quad(lambda z: (x[j+1] - z) * f(z), x[j], x[j+1])[0]) / h[j]

# print(A)
# print(rhs)
y_coef = np.linalg.solve(A, rhs)

# print(y_coef)

def y(t):
    return sum(y_coef[j-1] * phi_j(j)(t) for j in range(1, N-1))

print(y(1))