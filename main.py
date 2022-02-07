import numpy as np
import json
import matplotlib.pyplot as plt

class RawSubplotData():
    def __init__(self, pltype, x, y, xerr, yerr, axes_labels, axes_pupils, color, description):
        self.type = pltype
        self.color = color
        self.x = x
        self.y = y
        self.xerr = xerr
        self.yerr = yerr
        self.axes_labels = axes_labels
        self.axes_pupils = axes_pupils
        self.color = color
        self.description = description
    
    def print(self):
        print("type: ",        self.pltype,       '\n',
              "x: ",           self.x,            '\n',
              "y: ",           self.y,            '\n',
              "xerr: ",        self.xerr,         '\n',
              "yerr: ",        self.yerr,         '\n',
              "axes_labels: ", self.axes_labels,  '\n',
              "axes_pupils: ", self.axes_pupils,  '\n',
              "color: ",       self.color,        '\n',
              "description: ", self.description,  '\n')

class JsonParser:
    @classmethod
    def read(self, filename):
        with open(filename, "r") as read_file:
            data = json.load(read_file)
        return data

    @classmethod
    def parse_object(self, data):
        plots = []
        for i, plot in enumerate(data["data"], start=0):
            plots.append([])
            subplots = plot["subplots"]
            for subplot in subplots:
                plots[i].append(JsonParser.parse_subplot(subplot)) 
        return plots

    @classmethod
    def parse_subplot(self, subplot):
        pltype = subplot["type"]
        x = np.array(subplot["x"])
        y = np.array(subplot["y"])
        xerr = np.array(subplot["xerr"])
        yerr = np.array(subplot["yerr"])
        axes_labels = subplot["axes_labels"]
        axes_pupils = subplot["axes_pupils"]
        color = subplot["color"]
        description = subplot["description"]
        return RawSubplotData(pltype, x, y, xerr, yerr, axes_labels, axes_pupils, color, description)

class Plotter:
    @classmethod
    def plot(self, plots):
        for plot in plots:
            for subplot in plot:
                Plotter.plot_subplot(subplot)

    @classmethod
    def plot_subplot(self, s):
        if (s.type == 'lsq'):
            A = np.vstack([s.x, np.ones(len(s.y))]).T
            k, b = np.linalg.lstsq(A, s.y, rcond=None)[0]
            plt.plot(s.x, k*s.x+b, color=s.color, label=s.description)
            plt.errorbar(s.x, s.y, s.yerr, s.xerr, fmt='o', markersize=3, color=s.color, ecolor='black', capsize=5)
            plt.xlabel(s.axes_labels[0] + ', ' + s.axes_pupils[0], fontsize=15)
            plt.ylabel(s.axes_labels[1] + ', ' + s.axes_pupils[1], fontsize=15)
            plt.legend()
            plt.show()

data = JsonParser.read("conf.json")
plots = JsonParser.parse_object(data)
Plotter.plot(plots)
