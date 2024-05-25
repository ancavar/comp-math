import numpy as np
from scipy.integrate import quad
import matplotlib.pyplot as plt

λ = 1

def p(x):
    return 1

def q(x):
    return λ

def f(x):
    return -2 * λ * np.sin(np.sqrt(λ) * x)

def y_exact(x):
    return np.sin(np.sqrt(λ) * x)

def phi_j(j, x, N):
    h = x[j] - x[j-1]

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

def find_coeffs(x, N, h):
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

        rhs[i] = (quad(lambda z: (z - x[j-1]) * (-f(z)), x[j-1], x[j])[0] + quad(lambda z: (x[j+1] - z) * (-f(z)), x[j], x[j+1])[0]) / h[j]

    return np.linalg.solve(A, rhs)

def y_approx(y_coeffs, x, N):
    def y(t):
        return sum(y_coeffs[j-1] * phi_j(j, x, N)(t) for j in range(1, N))
    return y

# todo: too many args, name shadowing
def calculate_error(L, N, h, x, y_approx):
    left = norm_L(lambda x: y_exact(x) - y_approx(x), L)

    # ????
    c_1 = 20
    # harcoded bad
    Q = λ
    P_1 = 0
    P = 1

    c = (1 / c_1) * ((Q * L / 2 + P_1) * L / (2 * c_1) + 1)
    c_prime = np.sqrt(P + Q * L ** 2 / 4)
    norm_f = norm_L(f, L)
    right = (c * c_prime) ** 2 * h[0] ** 2 * norm_f
    
    result = "✅" if (right - left > 0) else "❌"
    
    print(f'λ = {λ}, N = {N}')
    print(f'Полученная = {left}, ожидаемая = {right} -- {result}')

def norm_L(func, L):
    return np.sqrt(quad(lambda x: func(x)**2, 0, L)[0])

def main(): 
    global λ

    Ns = [10, 100, 1000, 10000]
    for λ in range(1, 5):
        λ **= 2
        for idx, N in enumerate(Ns, start = 1):        
            a, b = 0, 2*np.pi
            x = np.linspace(a, b, N+1)
            h = np.diff(x)
            y_coeffs = find_coeffs(x, N, h)
            y = y_approx(y_coeffs, x, N)
            calculate_error(b, N, h, x, y)
            # plot_functions(a, b, y, N)


# def plot_functions(a, b, y, N):
#     x = np.linspace(a, b, (N+1)*10)
#     ys = [y(xs) for xs in x ]
#     ys_orig = [y_exact(xs) for xs in x]
#     plt.figure(figsize=(8, 6))
#     plt.plot(x, np.c_[ys_orig, ys], label=['sin(√λx)', 'approximation'])
#     plt.legend()
#     plt.xlabel('x')
#     plt.ylabel('y')
#     plt.savefig('func.png')


if __name__ == "__main__":
    main()
