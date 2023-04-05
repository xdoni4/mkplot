import sympy
from sympy.parsing.sympy_parser import parse_expr
import autograd.numpy as np
from autograd import grad


class Gradient:
    func_dict = {"exp":     np.exp,
                 "log":     np.log,
                 "sin":     np.sin,
                 "cos":     np.cos,
                 "tan":     np.tan,
                 "sinh":    np.sinh,
                 "cosh":    np.cosh,
                 "tanh":    np.tanh
    }

    def __init__(self, func_nm, expr, symbols, n_variables):
        self.symbols = [sympy.symbols(symbols)]
        self.expr = parse_expr(expr)
        self.func_nm = parse_expr(func_nm)
        self.f = sympy.lambdify(self.symbols, self.expr, self.func_dict)
        self.n_variables = n_variables

    def compute(self, constants, points):
        assert self.n_variables == points.shape[1]
        grads = np.array([]).reshape(0, points.shape[1])
        for i in range(points.shape[0]):
            grads = np.concatenate([grads, grad(self.f)(np.concatenate([points[i],
                                                                        constants]))[:self.n_variables].reshape(1, -1)])
        return grads

    def latex_derivatives(self):
        with open("generated_files/derivatives.tex", "a") as f:
            func_nm_latex = sympy.latex(self.func_nm)
            expr_latex = sympy.latex(self.expr)
            f.write('$' + func_nm_latex + ' = ' + expr_latex + ' \\\\$\n\n')
            for i in range(self.n_variables):
                symbol = self.symbols[0][i]
                partial = sympy.diff(self.expr, symbol)
                symbol_latex = sympy.latex(symbol)
                partial_latex = sympy.latex(partial)
                f.write('$\\frac{\\partial ' + func_nm_latex +
                        ' }{\\partial ' + symbol_latex +
                        '} = ' + partial_latex + ' \\\\$\n\n')

    def sigma_f(self, constants_eval, points, variable_errors):
        func_nm_latex = sympy.latex(self.func_nm)
        with open("generated_files/derivatives.tex", "a") as f:
            f.write('$\\sigma_' + func_nm_latex + ' = \\sqrt{')
            for i in range(self.n_variables):
                symbol = self.symbols[0][i]
                symbol_latex = sympy.latex(symbol)
                f.write('\\left(\\frac{\\partial ' + func_nm_latex +
                        ' }{\\partial ' + symbol_latex +
                        '}\\right)^2 \\sigma_' + symbol_latex + '^2')
                if i != self.n_variables - 1:
                    f.write(' + ')
            f.write('}\\\\$\n\n')
        grads = self.compute(constants_eval, points)
        return np.sqrt(((grads ** 2) * (variable_errors ** 2)).sum(axis=1))




