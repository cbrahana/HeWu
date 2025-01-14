"""
Zhai Jinpeng, 翟锦鹏, 2022
Contact: 914962409@qq.com

implements the Brode, 1978 model from the book:
PSR Report 1419-3
"AIRBLAST FROM NUCLEAR BURSTS—ANALYTIC APPROXIMATIONS"
Harold L. Brode, July 1987
Technical Report
CONTRACT No. DNA 001-85-C-0089  

Specifically, the below came from SECTION 4.
"""
from math import log10, exp


def _DeltaP_s(GR, H, W):
    """
    Peak overpressure in psi

    GR: ground range, in ft
    H: height, in ft
    W: yield, kT

    """
    m = W ** (1 / 3)
    x = GR / m / 1000
    y = H / m / 1000

    r = (x**2 + y**2) ** 0.5

    z = y / x

    a = 1.22 - 3.908 * z**2 / (1 + 810.2 * z**5)
    b = (
        2.321
        + 6.195 * z**18 / (1 + 1.113 * z**18)
        - 0.03831 * z**17 / (1 + 0.02415 * z**17)
        + 0.6692 / (1 + 4164 * z**8)
    )
    c = 4.153 - 1.149 * z**18 / (1 + 1.641 * z**18) - 1.1 / (1 + 2.771 * z**2.5)
    d = -4.166 + 25.76 * z**1.75 / (1 + 1.382 * z**18) + 8.257 * z / (1 + 3.219 * z)
    e = 1 - 0.004642 * z**18 / (1 + 0.003886 * z**18)
    f = (
        0.6096
        + 2.879 * z**9.25 / (1 + 2.359 * z**14.5)
        - 17.15 * z**2 / (1 + 71.66 * z**3)
    )
    g = 1.83 + 5.361 * z**2 / (1 + 0.3139 * z**6)

    h = (
        8.808 * z**1.5 / (1 + 154.5 * z**3.5)
        - (0.2905 + 64.67 * z**5) / (1 + 441.5 * z**5)
        - 1.389 * z / (1 + 49.03 * z**5)
        + 1.094
        * r**2
        / ((781.2 - 123.4 * r + 37.98 * r**1.5 + r**2) * (1 + 2 * y))
    )

    j = 0.000629 * y**4 / (3.493e-9 + y**4) - 2.67 * y**2 / (1 + 1e7 * y**4.3)
    k = 5.18 + 0.2803 * y**3.5 / (3.788e-6 + y * 4)

    return 10.47 / r**a + b / r**c + d * e / (1 + f * r**g) + h + j / r**k


def _T(GR, H, W):
    """
    close-in time of arrival versus shock radius, in millisecond, eq.41
    intended as a helper function for DeltaP

    "is valid for 1e-3 < T < 26,000 ms at 1 KT. This more complex fit is
     advisable for pressures above 10,000 psi, or scaled times less
     than 0.6 ms/KT^(1/3). For a surface burst, use m = (2W)^(1/3)."


    GR: ground range in ft
    H: height in ft
    W: yield in kt

    """

    m = W ** (1 / 3)
    r = (GR**2 + H**2) ** 0.5 / m / 1000

    a = (0.543 - 21.8 * r + 386 * r**2 + 2383 * r**3) * r**8
    b = 1e-6 * (2.99e-8 - 1.91e-4 * r**2 + 1.032 * r**4 - 4.43 * r**6)
    c = (1.028 + 2.087 * r + 2.69 * r**2) * r**8

    return m * a / (b + c)


def _DeltaP(GR, H, W, t):
    """
    Overpressure over time in psi, eq.61. Result is complex if supplied time
    is less than that of blast arrival time. Verified against graphs in the
    original work to be in excellent agreement.

    GR: ground range in feet
    H: burst height in feet
    W: yield in kiloton
    t: time in seconds

    """
    m = W ** (1 / 3)
    X = GR / m  # ft/kT^(1/3)
    Y = H / m  # ft/kT^(1/3)

    z = H / GR

    sigma = t * 1000  # presumably, in ms

    Xm = (
        170 * Y / (1 + 60 * Y**0.25) + 2.89 * (Y / 100) ** 2.5
    )  # onset of Mach reflection locus, scaled, in ft per kT**(1/3)

    Xe = (
        3.039 * Y / (1 + 0.0067 * Y)
    )  # locus of points where second peak equals first peak, scaled in ft per kT**(1/3)

    K = abs((X - Xm) / (Xe - Xm))
    d2 = 2.99 + 31240 * (Y / 100) ** 9.86 / (1 + 15530 * (Y / 100) ** 9.87)

    d = (
        0.23
        + 0.583 * Y**2 / (26667 + Y**2)
        + 0.27 * K
        + (0.5 - 0.583 * Y**2 / (26667 + Y**2)) * K**d2
    )

    a = (d - 1) * (1 - K**20 / (1 + K**20))

    r = (X**2 + Y**2) ** 0.5 / 1000
    # rm = (Xm**2 + Y**2) ** 0.5 / 1000  # assumedly, this eq is missing from original

    # scaled time of arrival in milliseconds per cube-root kiloton, based on Eq. (41),
    if X <= Xm:
        # tau = _u(r) # _u equivalent to _T for 1kT
        tau = _T(GR, H, 1)
    else:
        # tau = _u(rm) + _w(r) - _w(rm) # _w equivalent to _T for 2kT
        tau = _T(Xm * m, H, 1) + _T(GR, H, 2) - _T(Xm * m, H, 2)

    s2 = (
        1
        - 15.18 * (Y / 100) ** 3.5 / (1 + 15.18 * (Y / 100) ** 3.5)
        - 0.02441
        * (Y / 1e6) ** 2
        / (1 + 9000 * (Y / 100) ** 7)
        * 1e10
        / (0.441 + (X / 100) ** 10)
    )

    D = (
        (1640700 + 24629 * tau + 416.15 * tau**2)
        / (10880 + 619.76 * tau + tau**2)
        * (
            0.4
            + 0.001204 * tau**1.5 / (1 + 0.001559 * tau**1.5)
            + (
                0.6126
                + 0.5486 * tau**0.25 / (1 + 0.00357 * tau**1.5)
                - 3.47 * tau**0.637 / (1 + 5.696 * tau**0.645)
            )
            * s2
        )
    )  # duration of positive phase in milliseconds,

    s = (
        1
        - 1100 * (Y / 100) ** 7 / (1 + 1100 * (Y / 100) ** 7)
        - 2.441e-14
        * Y**2
        / (1 + 9000 * (Y / 100) ** 7)
        * 1e10
        / (0.441 + (X / 100) ** 10)
    )

    f2 = (
        (
            0.445
            - 5.44 * r**1.02 / (1 + 100000 * r**5.84)
            + 7.571 * z**7.15 / (1 + 5.135 * z**12.9)
            - 8.07 * z**7.31 / (1 + 5.583 * z**12.23)
        )
        * 0.4530
        * (Y / 10) ** 1.26
        / (1 + 0.03096 * (Y / 10) ** 3.12)
        * (1 - 0.000019 * tau**8 / (1 + 0.000019 * tau**8))
    )

    f = (
        (
            0.01477 * tau**0.75 / (1 + 0.005836 * tau)
            + 7.402e-5 * tau**2.5 / (1 + 1.429e-8 * tau**4.75)
            - 0.216
        )
        * s
        + 0.7076
        - 3.077e-5 * tau**3 / (1 + 4.367e-5 * tau**3)
        + f2
        - (0.452 - 9.94e-7 * X**4.13 / (1 + 2.1868e-6 * X**4.13))
        * (1 - 0.00015397 * Y**4.3 / (1 + 0.00015397 * Y**4.3))
    )

    g = (
        10 + (77.58 - 64.99 * tau**0.125 / (1 + 0.04348 * tau**0.5)) * s
    )  # early time decay power

    h = (
        3.003
        + 0.05601 * tau / (1 + 1.473e-9 * tau**5)
        + (
            0.01769 * tau / (1 + 3.207e-10 * tau**4.25)
            - 0.03209 * tau**1.25 / (1 + 9.914e-8 * tau**4)
            - 1.6
        )
        * s
        - 0.1966 * tau**1.22 / (1 + 0.767 * tau**1.22)
    )

    j = min(
        11860 * (sigma - tau) / (Y * abs(X - Xm) ** 1.25), 200
    )  # ratio of time after TOA to time to second peak after TOA,
    # this absolute operation around X-Xm is inferred.

    v = 1 + (
        0.003744 * (Y / 10) ** 5.185 / (1 + 0.004684 * (Y / 10) ** 4.189)
        + 0.004755 * (Y / 10) ** 8.049 / (1 + 0.003444 * (Y / 10) ** 7.497)
        - 0.04852 * (Y / 10) ** 3.423 / (1 + 0.03038 * (Y / 10) ** 2.538)
    ) * j**3 / (6.13 + j**3) / (1 + 9.23 * K**2)

    c2 = 23000 * (Y / 100) ** 9 / (1 + 23000 * (Y / 100) ** 9)
    c3 = 1 + (
        1.094
        * K**0.738
        / (1 + 3.687 * K**2.63)
        * (1 - 83.01 * (Y / 100) ** 6.5 / (1 + 172.3 * (Y / 100) ** 6.04))
        - 0.15
    ) / (1 + 0.5089 * K**13)

    c = (
        (
            (1.04 - 0.02409 * (X / 100) ** 4 / (1 + 0.02317 * (X / 100) ** 4))
            * j**7
            / ((1 + a) * (1 + 0.923 * j**8.5))
        )
        * (c2 + (1 - c2) * (1 - 0.09 * K**2.5 / (1 + 0.09 * K**2.5)))
        * c3
        * (1 - ((sigma - tau) / D) ** 8)
    )

    b = (f * (tau / sigma) ** g + (1 - f) * (tau / sigma) ** h) * (
        1 - (sigma - tau) / D
    )

    if X >= Xm and Y <= 380:
        return _DeltaP_s(GR, H, W) * (1 + a) * (b * v + c)
    else:
        return _DeltaP_s(GR, H, W) * b


def _Q_1(x, y, xq):
    """
    helper function for _Q_s
    """

    r = (x**2 + y**2) ** 0.5
    M = xq / x

    A = -236.1 + 17.72 * M**0.593 / (1 + 10.4 * M**3.124)
    B = 12.27 - 21.69 * M**2.24 / (1 + 6.976 * M**0.484)
    C = 20.26 + 14.7 * M**2 / (1 + 0.08747 * M**3.05)
    D = -1.137 - 0.5606 * M**0.895 / (1 + 3.046 * M**7.48)
    E = 1.731 + 10.84 * M**1.12 / (1 + 12.26 * M**0.0014)
    F = 2.84 + 0.855 * M**0.9 / (1 + 1.05 * M**2.84)

    return A * r**D / (1 + B * r**E) + C / r**F


def _Q_s(GR, H, W):
    """
    Peak (horizontal) dynamic pressure in psi

    GR: ground range, feet
    H: burst height, feet
    W: yield, kiloton
    """
    m = W ** (1 / 3)
    x = GR / 1000 / m  # scaled ground range in kft/kt^1/3
    y = H / 1000 / m  # scaled ground range in kft/kft^1/3

    r = (x**2 + y**2) ** 0.5

    xq = (
        63.5 * y**7.26 / (1 + 67.11 * y**4.746) + 0.6953 * y**0.808
    )  # approximate interface between regular and Mach reflection in kft/kt^(1/3)

    Q1 = _Q_1(x, y, xq)
    Qm = _Q_1(xq, y, xq)  # Q_1 evaluated at x=xq, and M = 1

    G = 50 - 1843 * y**2.153 / (1 + 3.95 * y**5.08)
    H = 0.294 + 71.56 * y**8.7 / (1 + 115.3 * y**6.186)
    I = abs(-3.324 + 987.5 * y**4.77 / (1 + 211.8 * y**5.166))
    J = 1.955 + 169.7 * y**9.317 / (1 + 97.36 * y**6.513)
    K = 8.123e-6 + 0.001613 * y**6.428 / (1 + 60.26 * y**7.358)
    L = log10(xq / x)

    if x >= xq:
        return Q1
    else:
        return Qm * exp(
            G * L**I / (1 + 649 * L**I)
            - 4.01 * L**J / (1 + H * L**J)
            + 7.67e-6 * (1 / (K + L**3.22) - 1 / K)
        )


if __name__ == "__main__":
    print(_Q_s(350, 250, 1))
