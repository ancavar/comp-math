import numpy as np

# credit: https://github.com/zlliang/jacobi-svd/blob/master/presentation.pdf

def jacobi(alpha, beta, gamma):
    if beta != 0:
        tau = (gamma - alpha) / (2 * beta)
        if tau >= 0:
            t = 1 / (tau + np.sqrt(1 + tau**2))
        else:
            t = -1 / (-tau + np.sqrt(1 + tau**2))
        c = 1 / np.sqrt(1 + t**2)
        s = t * c
    else:
        c = 1
        s = 0
        t = 0
    return c, s, t

def construct_G(c, s):
    G = np.array([[c, s], [-s, c]])
    return G

def qr_algo(A):
    m, n = A.shape
    Q, R = np.linalg.qr(A)
    R = R[:n, :n]
    k = np.argmax(np.abs(np.diag(R)) < np.finfo(float).eps * np.linalg.norm(R, ord='fro'))
    if k < n:
        Q1, R1 = np.linalg.qr(R.T)
        U1, sigma, V1 = jacobi_svd(R1.T)
        # ??????
        _, sigma, _ = jacobi_svd(R.T)
        U = np.dot(Q, U1)

        V = np.dot(Q1, V1)
        return U, sigma, V

def jacobi_svd(A):
    m, n = A.shape
    tol = 1e-14
    rots = 1
    sigma = np.sum(A**2, axis=0)
    V = np.eye(n)
    i = j = 0
    tolsigma = tol * np.linalg.norm(A, 'fro')

    while rots >= 1:
        i += 1
        rots = 0
        for p in range(n - 1):
            for q in range(p + 1, n):
                beta = np.dot(A[:, p].T, A[:, q])
                if sigma[p] * sigma[q] > tolsigma and abs(beta) >= tol * np.sqrt(sigma[p] * sigma[q]):
                    j += 1
                    rots += 1
                    c, s, t = jacobi(sigma[p], beta, sigma[q])
                    G = construct_G(c, s)

                    sigma[p] -= beta * t
                    sigma[q] += beta * t
                    A[:, [p, q]] = A[:, [p, q]] @ G
                    V[:, [p, q]] = V[:, [p, q]] @ G

    indices = np.argsort(-sigma)
    sigma = np.sqrt(sigma[indices])
    U = A[:, indices]
    V = V[:, indices]
    U /= sigma
    return U, sigma, V

def jacobi_method(A):
    U, sigma, V = qr_algo(A)
    return U, sigma, V.T
