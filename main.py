from plotting import *

data, xl = Parser.read("conf.json")
plots = Parser.parse_object(data, xl)
Plotter.plot(plots)
