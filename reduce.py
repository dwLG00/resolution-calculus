from predicate_logic import *
from helper import RecursiveFlag

def replace(term, var, repl):
    # repl must be an atomic function that returns an instance. For example, a callable (variable, constant)
    # or a function that constructs an instance, e.g. lambda _: f(x(), y(), z())
    if term.isa(var):
        return repl()

    if term.isa(Variable) or term.isa(Constant):
        return term

    # Prevent replacing closed variables with non-variables
    if term.isa(Quantifier):
        qvar = term.children[0]
        if qvar.isa(var) and not repl().isa(Variable):
            raise Exception("Can't replace closed variable (=variable used in quantifier) with non-variable")

    return term.base.instance(*(replace(child, var, repl) for child in term.children))

def alpha(term, verbose=False):
    A = not_(term)
    flag = RecursiveFlag()
    history = [A]

    A = alpha_helper(history[-1], flag)
    while flag:
        flag.reset()
        history.append(A)
        A = alpha_helper(history[-1], flag)

    if verbose:
        return history
    return history[-1]

def alpha_helper(term, recursive_flag):
    # Root-level Substitution
    if term.isa(If):
        F1, F2 = term.children
        return or_(not_(F1), F2)

    if term.isa(Not):
        subterm = term.children[0]
        if subterm.isa(And):
            F1, F2 = subterm.children
            recursive_flag.toggle()
            return or_(not_(F1), not_(F2))
        if subterm.isa(Or):
            F1, F2 = subterm.children
            recursive_flag.toggle()
            return and_(not_(F1), not_(F2))
        if subterm.isa(Not):
            F = subterm.children[0]
            recursive_flag.toggle()
            return F
        if subterm.isa(Forall):
            x, F = subterm.children #x is an instance!
            recursive_flag.toggle()
            return exists(x, not_(F))
        if subterm.isa(Exists):
            x, F = subterm.children #x is an instance!
            recursive_flag.toggle()
            return forall(x, not_(F))

    # Recursive Substitution
    if term.isa(BinOp):
        F1, F2 = term.children
        return term.base.instance(alpha_helper(F1, recursive_flag), alpha_helper(F2, recursive_flag))

    if term.isa(Not):
        F = term.children[0]
        return not_(alpha_helper(F, recursive_flag))

    if term.isa(Quantifier):
        x, F = term.children
        return term.base.instance(x, alpha_helper(F, recursive_flag))

    #variable, constant, function, or proposition
    return term

def beta(term, generate_function, generate_constant):
    flag = RecursiveFlag()
    new_term = beta_helper(term, generate_function, generate_constant, flag)
    while flag:
        flag.reset()
        new_term = beta_helper(new_term, generate_function, generate_constant, flag)
    return new_term

def beta_helper(term, generate_function, generate_constant, recursive_flag):
    # find first Exists quantifier
    first_exists_path = find_first_exists(term)
    if not first_exists_path:
        return term

    recursive_flag.toggle()

    dependent_foralls = tuple(term for term in first_exists_path if term.isa(Forall))
    first_exists_var, _ = first_exists_path[-1].children

    # omit the first exists
    if len(first_exists_path) == 1: #root term is the first exists -> just skip it
        term = term.children[1]
    else:
        omit_first_exists(first_exists_path[-1], first_exists_path[-2])

    if len(dependent_foralls) == 0: # Case: Exists isn't dependent on any foralls
        new_constant = generate_constant()
        return replace(term, first_exists_var.base, new_constant)
    #Case: Exists is dependent on some number of foralls
    dependent_vars = tuple(forall.children[0].base for forall in dependent_foralls)
    new_function = generate_function(len(dependent_vars))
    repl = lambda: new_function(*(var() for var in dependent_vars))
    return replace(term, first_exists_var.base, repl)

def find_first_exists(term):
    # returns a tuple "path" leading to first exists term, or None
    if term.isa(Exists):
        return (term,)

    if len(term.children) == 0:
        return None

    for child in term.children:
        first_exists = find_first_exists(child)
        if first_exists:
            return (term,) + first_exists

    return None

def omit_first_exists(first_exists, parent):
    '''Modifies statement in place to omit first_exists from parent, instead swapping it with its own subterm'''
    _, subterm = first_exists.children
    omitted_children = (child if not (child is first_exists) else subterm for child in parent.children)
    parent.children = tuple(omitted_children)
