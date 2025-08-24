# iLaplace

> A Simple Interface for Powerful Math

`iLaplace` is a lightweight Python wrapper around advanced symbolic and numerical math tools (`sympy`, `numpy` & `mpmath`) that provides a clean and intuitive interface for computing inverse Laplace transforms using Talbot's method.

I created this library to simplify the process of using the inverse Laplace transform, aiming to provide a **MATLAB-like experience within Python**. This means the output of my code in Python will be compared against a sample calculation in MathWorks MATLAB.

-----

## Why This Library?

If you've ever tried to compute inverse Laplace transforms numerically in Python, you've probably noticed:

  * `mpmath.invertlaplace()` is powerful but raw and low-level.
  * `sympy` gives symbolic transforms, but not numerical answers.
  * Combining them can be verbose and repetitive.

**In short: You focus on the math, we handle the machinery.**

-----

## MATLAB vs. Python Comparison

Here is a sample calculation in MATLAB and its equivalent in Python using this library.

### MATLAB Example

```matlab
syms s t

X = (s+3)/((s+1)^2 * (s^2+9));

V = vpa(ilaplace(X, s, t));

t0   = 5.2643;
Volt = double(subs(V, t, t0));

disp(Volt)
```

The output in MATLAB is `0.1474`.

### Python Equivalent with iLaplace

```python
import iLaplace as il
import sympy as sp

t, s = sp.symbols('t s')

X = (s+3)/((s+1)**2 * (s**2+9))

t0 = 5.2643
Answer = il.inverse_laplace(X, t0)

print(Answer)
```

And the output is `0.1473`. To be more precise:

```
0.1473626511069924
```

-----

## License and Attributions

This project is licensed under the MIT License.

It internally utilizes components from the following libraries: `mpmath` & `sympy`.

All third-party libraries retain their original licenses and attributions.