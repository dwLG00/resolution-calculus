import inspect

class PL:
    def __init__(self, vars, constants, functions, predicates):
        self.V = vars
        self.CS = constants
        self.FS = functions
        self.PS = predicates

    def is_valid(self, term):
        pass

class Instance:
    def __init__(self, base):
        self.base = base
        self.children = []

    def isa(self, baseobj):
        # Checks if is instance of particular semantic class
        if inspect.isclass(baseobj) and inspect.isclass(self.base):
            return issubclass(self.base, baseobj)
        if inspect.isclass(baseobj):
            return isinstance(self.base, baseobj)
        if inspect.isclass(self.base): #instance derived from class checked against an object-type
            return False
        return self.base is baseobj

    def __eq__(self, term):
        # Checks if instance shares base with other instance
        if isinstance(term, Instance):
            return self.base is term.base
        return False

class VariableInstance(Instance):
    def __str__(self):
        return self.base.name

class ConstantInstance(Instance):
    def __str__(self):
        return self.base.name

class FunctionInstance(Instance):
    def __init__(self, base, arguments):
        self.base = base
        self.children = arguments

    def __str__(self):
        argstring = ', '.join(str(arg) for arg in self.children)
        return '%s(%s)' % (self.base.name, argstring)

class PredicateInstance(Instance):
    def __init__(self, base, arguments):
        self.base = base
        self.children = arguments

    def __str__(self):
        argstring = ', '.join(str(arg) for arg in self.children)
        return '%s(%s)' % (self.base.name, argstring)

class QuantifierInstance(Instance):
    def __init__(self, base, variable, term):
        self.base = base
        self.children = (variable, term)

    def __str__(self):
        return '(%s%s)%s' % (self.base.symbol, str(self.children[0]), str(self.children[1]))

class BinOpInstance(Instance):
    def __init__(self, base, arg1, arg2):
        self.base = base
        self.children = (arg1, arg2)

    def __str__(self):
        return '(%s %s %s)' % (str(self.children[0]), self.base.symbol, str(self.children[1]))

class NotInstance(Instance):
    def __init__(self, base, arg):
        self.base = base
        self.children = (arg,)

    def __str__(self):
        return '¬%s' % str(self.children[0])

class Instantiable:
    def instance(self, *args, **kwargs):
        return

    def __call__(self, *args, **kwargs):
        return self.instance(*args, **kwargs)

class Variable(Instantiable):
    def __init__(self, name):
        self.name = name

    def instance(self):
        return VariableInstance(self)

    @staticmethod
    def occurs(term, variable):
        '''Recursively checks if variable is in term'''
        if len(term.children) == 0:
            return False
        if variable in term.children:
            return True
        if any(occurs(subterm, variable) for subterm in term.children):
            return True

class Constant(Instantiable):
    def __init__(self, name):
        self.name = name

    def instance(self):
        return ConstantInstance(self)

class Function(Instantiable):
    def __init__(self, name, nargs):
        self.name = name
        self.nargs = nargs

    def instance(self, *arguments):
        assert len(arguments) == self.nargs
        return FunctionInstance(self, arguments)

class Predicate(Instantiable):
    def __init__(self, name, nargs):
        self.name = name
        self.nargs = nargs

    def instance(self, *arguments):
        assert len(arguments) == self.nargs
        return PredicateInstance(self, arguments)

class Quantifier:
    @classmethod
    def instance(cls, variable, term):
        return QuantifierInstance(cls, variable, term)

    @classmethod
    def looseinstance(cls, variable):
        return QuantifierInstance(cls, variable, None)

    @staticmethod
    def match_quantifier(term, looseinstance):
        if term.isa(looseinstance.base) and term.children[0].base is looseinstance.children[0].base:
            return True
        return False

    @staticmethod
    def occurs(term, looseinstance):
        if Quantifier.match_quantifier(term, looseinstance): return True
        if term.isa(Quantifier):
            return Quantifier.occurs(term.children[1], looseinstance)
        if term.isa(BinOp):
            return Quantifier.occurs(term.children[0], looseinstance) or Quantifier.occurs(term.children[1], looseinstance)
        if term.isa(Not):
            return Quantifier.occurs(term.children[0], looseinstance)
        return False

    @staticmethod
    def before(term, q1, q2): # returns true if q1 < q2, false if q2 < q1, None otherwise
        if Quantifier.match_quantifier(term, q2):
            if Quantifier.occurs(term, q1): return True
            return None
        if Quantifier.match_quantifier(term, q1):
            if Quantifier.occurs(term, q2): return False
            return None

        if term.isa(Quantifier):
            return Quantifier.before(term.children[1], q1, q2)

        if term.isa(BinOp):
            if (res := Quantifier.before(term.children[0], q1, q2)) != None:
                return res
            if (res := Quantifier.before(term.children[1], q1, q2)) != None:
                return res

        if term.isa(None):
            if (res := Quantifier.before(term.children[0], q1, q2)) != None:
                return res

        return None

class Forall(Quantifier):
    symbol = '∀'

class Exists(Quantifier):
    symbol = '∃'

class BinOp:
    @classmethod
    def instance(cls, arg1, arg2):
        return BinOpInstance(cls, arg1, arg2)

class And(BinOp):
    symbol = '∧'

class Or(BinOp):
    symbol = '∨'

class If(BinOp):
    symbol = '→'

class Not:
    @classmethod
    def instance(cls, arg):
        return NotInstance(cls, arg)

# Aliases
forall = Forall.instance
exists = Exists.instance
and_ = And.instance
or_ = Or.instance
if_ = If.instance
not_ = Not.instance
