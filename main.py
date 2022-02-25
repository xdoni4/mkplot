import numpy as np
import json
import os
import matplotlib
import matplotlib.pyplot as plt
# from PIL import Image
# matplotlib.use('Qt5Agg')

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
            array = []
            subplots = plot["subplots"]
            for subplot in subplots:
                array.append(JsonParser.parse_subplot(subplot)) 
            plots.append((array, plot["title"]))
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
        self.makedirs()
        fig = plt.figure()
        axes = [] 
        for i, plot in enumerate(plots):
            f = open("generated_files/coefs.txt", 'a') 
            f.write(plot[1] + '\n\n')
            f.close()
            axes.append(fig.add_subplot(1, len(plots), i+1))
            for subplot in plot[0]:
                Plotter.plot_subplot(axes[i], subplot)
            axes[i].set_title(plot[1])  
        f = open("generated_files/coefs.txt", 'a') 
        f.write('-----------------------------------------------------\n\n')
        img = open("images/fig.png", 'w')
        plt.show()
        fig.savefig("images/fig.png") 

    @classmethod
    def plot_subplot(self, ax, s):
        # ax.scatter(0, 0, color='white') 
        ax.minorticks_on()
        ax.grid(True, which='major', linewidth=1)
        ax.grid(True, which='minor', linewidth=0.5)
        ax.set_xlabel(s.axes_labels[0] + ', ' + s.axes_pupils[0], fontsize=15)
        ax.set_ylabel(s.axes_labels[1] + ', ' + s.axes_pupils[1], fontsize=15) 
        r = np.linspace(0, 1.2*s.x[len(s.x)-1]) 

        f = open("generated_files/coefs.txt", 'a')
        if (s.type == 'lsq'):
            A = np.vstack([s.x, np.ones(len(s.y))]).T
            k, b = np.linalg.lstsq(A, s.y, rcond=None)[0] 
            sigma_k, sigma_b = Plotter.sigma_eval(s.x, s.y, k, b) 
            f.write("lsq"+ ' ' + s.color+ ': k=' + str(k) + ' b='+str(b) + ' sigma_k='+str(sigma_k)+' sigma_b='+str(sigma_b)+'\n\n')
            ax.plot(r, k*r+b, color=s.color, label=s.description, linewidth=1)
            ax.errorbar(s.x, s.y, s.yerr, s.xerr, fmt='o', markersize=3, linewidth=1, color=s.color, ecolor='black', capsize=0)
        
        elif (s.type == 'log'):
            x = np.log(s.x)
            y = np.log(s.y)
            v = np.linspace(0, 1.2*x[len(x)-1])
            A = np.vstack([x, np.ones(len(y))]).T
            k, b = np.linalg.lstsq(A, y, rcond=None)[0] 
            sigma_k, sigma_b = Plotter.sigma_eval(x, y, k, b) 
            f.write("lsq"+ ' ' + s.color+ ': k=' + str(k) + ' b='+str(b) + ' sigma_k='+str(sigma_k)+' sigma_b='+str(sigma_b)+'\n\n')
            ax.plot(v, k*v+b, color=s.color, label=s.description, linewidth=1) 
            ax.errorbar(x, y, fmt='o', markersize=3, linewidth=1, color=s.color, ecolor='black', capsize=0)

        elif (s.type.rstrip('_0123456789') == 'poly'):
            coefs = np.polyfit(s.x, s.y, int(s.type.split('_')[1]))
            ys = np.zeros(len(r))
            for i, c in enumerate(coefs):
                ys += c * r ** (len(coefs)-i-1) 
            f.write("lsq"+ ' ' + s.color+ ":\n")
            for i, c in enumerate(coefs):
                f.write("a_"+str(len(coefs)-i-1) + "=" + str(c) + '\n')
            f.write('\n')
            ax.plot(r, ys, color=s.color, label=s.description, linewidth=1)
            ax.errorbar(s.x, s.y, s.yerr, s.xerr, fmt='o', markersize=3, linewidth=1, color=s.color, ecolor='black', capsize=0)
        ax.legend()
        f.close()
    
    @staticmethod 
    def makedirs():
        if not os.path.exists('generated_files'):
            os.mkdir('generated_files');
        # if os.path.exists('generated_files/coefs.txt'):
        #     with open("generated_files/coefs.txt", 'w') as fopen:
        #         fopen.close()
        fopen = open("generated_files/coefs.txt", 'a')
        fopen.write('-----------------------------------------------------\n\n')
        if not os.path.isdir('images'):
            os.mkdir('images')
    
    @classmethod
    def sigma_eval(self, x, y, k, b):
        xdisp = np.var(x)
        ydisp = np.var(y)
        sigma_k = np.sqrt((ydisp/xdisp - k ** 2) / (len(x)-2))
        sigma_b = sigma_k * np.sqrt(np.average(x * x))
        return (sigma_k, sigma_b)

data = JsonParser.read("conf.json")
plots = JsonParser.parse_object(data)
Plotter.plot(plots)
