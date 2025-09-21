### Resolver derivadas con sympy
import sympy as sp

x = sp.Symbol('x')
t = sp.Symbol('t')
s = sp.Symbol('s')
ys = sp.Symbol('y')
As = sp.Symbol('A')
Bs = sp.Symbol('B')
a = sp.Symbol('a')
b = sp.Symbol('b')
c = sp.Symbol('c')
v = sp.Symbol('v')

# 1. f(x) = 186.5
f = 186.5
df_dx = sp.diff(f, x)
print("f(x)= 186.5, f'(x)= ", df_dx)

# 2. f(t) = 2 - 2/3t
f = 2 - sp.Rational(2,3) * t
df_dt = sp.diff(f,t)
print("f(t)= 2 - 2/3t, f'(t)= ", df_dt)

# 3. f(x) = x^3 -4x +6
f = x**3 -4*x +6
df_dx = sp.diff(f,x)
print("f(x)= x**3 -4x +6, f'(x)= ", df_dx)

# 4. f(t) = 1/4(t^4 +8)
f = sp.Rational(1,4) * (t**4 +8)
df_dt = sp.diff(f,t)
print("f(t) = 1/4(t**4 +8), f'(t)= ", df_dt)

# 5. A(s) = -12/s^5
A = sp.Rational(-12, 1)/s**5
dA_ds = sp.diff(A,s)
print("A(s) = -12/s**5, f'(t)= ", dA_ds)

# 6. g(t) = 2t**(-3/4)
g = 2*t**(sp.Rational(-3,4))
dg_dt = sp.diff(g,t)
print("g(t) = 2t**(-3/4), f'(t)= ", dg_dt)

# 7. y = 3e**x + 4/x**(1/3)
y = 3 * sp.exp(x) + 4 * x**sp.Rational(-1,3)
dy_dx = sp.diff(y,x)
print("y = 3e**x + 4/x**(1/3), y' = ", dy_dx)

# 8. F(x) = (x/2)**5
F = (x/2)**5
dF_dx = sp.diff(F,x)
print("F(x) = (x/2)**5, F'(x) = ", dF_dx)

# 9. y = (x**2 + 4x +3) * x**(-1/2)
y = (x**2 + 4*x + 3) * x**(-1/2)
dy_dx = sp.diff(y,x)
print("y(x) = x**2 + 4x + 3, y'(x) = ", dy_dx)

# 10. y = 4 * pi**2
y = 4 * sp.pi**2
dy_dx = sp.diff(y,x)
print("y(x) = 4 * pi**2, y'(x) = ", dy_dx)

# 11 . u = t**(1/5) + 4*t**(5/2)
u = t**(1/5) + 4 * t ** (5/2)
du_dt = sp.diff(u,t)
print("u(t) = t**(1/5) + 4*t**(5/2), u'(t) = ", du_dt)

# 12. z = A*y**(-10) + Be**y
z = As*ys**(-10) + Bs * sp.exp(ys)
dz_dy = sp.diff(z,ys)
print("z(y) = A*y**(-10) + Be**y, z'(y) = ", dz_dy)

# 13. y = a*e**v + b/v + c*v**(-2)
y = a * sp.exp(v) + b/v + c*v**(-2)
dy_dv = sp.diff(y,v)
print("y(v) = a*e**v + b/v + c*v**(-2), y'(v) = ", dy_dv)

# 14. v(x) = (x**(1/2) + x**(-1/3))**2
v = (x**(1/2) + x**(sp.Rational(-1,3)))**2
dv_dx = sp.diff(v,x)
print("v(x) = (x**(1/2) + x**(-1/3))**2, v'(x) = ", dv_dx)

# 15. y(x) = e**(x+1) +1
y = sp.exp(x+1) +1
dy_dx = sp.diff(y,x)
print("y(x) = e**(x+1) +1, y'(x) = ", dy_dx)