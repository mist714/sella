import pytest
import numpy as np

from sella.utilities.math import pseudo_inverse, modified_gram_schmidt

from test_utils import get_matrix


# TODO: figure out why m > n crashes
@pytest.mark.parametrize("n,m,eps",
                         [(3, 3, 1e-10),
                          (100, 3, 1e-6),
                          ])
def test_mppi(n, m, eps):
    rng = np.random.RandomState(1)

    tol = dict(atol=1e-6, rtol=1e-6)

    A = get_matrix(n, m, rng=rng)
    U1, s1, VT1, Ainv, nsing1 = pseudo_inverse(A.copy(), eps=eps)

    A_test = U1[:, :nsing1] @ np.diag(s1) @ VT1[:nsing1, :]
    np.testing.assert_allclose(A_test, A, **tol)

    Ainv_test = np.linalg.pinv(A)
    np.testing.assert_allclose(Ainv_test, Ainv, **tol)

    nsingB = nsing1 - 1
    B = U1[:, :nsingB] @ np.diag(s1[:nsingB]) @ VT1[:nsingB, :]
    U2, s2, VT2, Binv, nsing2 = pseudo_inverse(B.copy(), eps=eps)


@pytest.mark.parametrize("n,mx,my,eps1,eps2,maxiter",
                         [(3, 2, 1, 1e-15, 1e-6, 100),
                          (100, 50, 25, 1e-15, 1e-6, 100),
                          ])
def test_modified_gram_schmidt(n, mx, my, eps1, eps2, maxiter):
    rng = np.random.RandomState(2)

    tol = dict(atol=1e-6, rtol=1e-6)
    mgskw = dict(eps1=eps1, eps2=eps2, maxiter=maxiter)

    X = get_matrix(n, mx, rng=rng)

    Xout1 = modified_gram_schmidt(X, **mgskw)
    _, nxout1 = Xout1.shape

    np.testing.assert_allclose(Xout1.T @ Xout1, np.eye(nxout1), **tol)
    np.testing.assert_allclose(np.linalg.det(X.T @ X),
                               np.linalg.det(X.T @ Xout1)**2, **tol)


    Y = get_matrix(n, my, rng=rng)
    Xout2 = modified_gram_schmidt(X, Y, **mgskw)
    _, nxout2 = Xout2.shape

    np.testing.assert_allclose(Xout2.T @ Xout2, np.eye(nxout2), **tol)
    np.testing.assert_allclose(Xout2.T @ Y, np.zeros((nxout2, my)), **tol)

    X[:, 1] = X[:, 0]

    Xout3 = modified_gram_schmidt(X, **mgskw)
    _, nxout3 = Xout3.shape
    assert nxout3 == nxout1 - 1

    np.testing.assert_allclose(Xout2.T @ Xout2, np.eye(nxout2), **tol)
