import numpy as np

def iterative_construction_of_q(A, iters):
    m, n = A.shape
    Q = np.zeros((m, 0))
    for i in range(iters):
        omega = np.random.normal(size=(n, 1))
        y = A @ omega
        q_tilde = y - Q @ Q.T @ y
        q = q_tilde / np.linalg.norm(q_tilde)
        Q = np.hstack((Q, q))
    return Q


def randomized_method(A, iters = 100):
    from power_svd import power_method
    Q = iterative_construction_of_q(A, iters) 
    B = Q.T @ A
    U_tilde, Sigma, VT = power_method(B)    
    U = Q @ U_tilde
    return U, Sigma, VT  
