from predicate_logic import *

CONSTANT_COUNTER = 1
FUNCTION_COUNTER = 1

x = Variable('x')
y = Variable('y')
u = Variable('u')
v = Variable('v')
z = Variable('z')
P = Predicate('P', 2)
Q = Predicate('Q', 2)

statement = forall(x(), exists(y(), and_(P(x(), y()), P(y(), x())))) #Any object x commutes with some object y wrt P
reduce_example = and_( #Page 13 Example 2.2.2
    or_(
        forall(x(), exists(y(), P(x(), y()))),
        forall(u(), exists(v(), not_(Q(u(), v()))))
    ),
    exists(z(), not_(P(z(), z())))
)

def generate_constant():
    global CONSTANT_COUNTER
    ret = Constant('c%s' % CONSTANT_COUNTER)
    CONSTANT_COUNTER += 1
    return ret

def generate_function(n):
    global FUNCTION_COUNTER
    ret = Function('f%s' % FUNCTION_COUNTER, n)
    FUNCTION_COUNTER += 1
    return ret
