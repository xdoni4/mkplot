import os
import matplotlib.pyplot as plt
from gradient import Gradient
from parsing import *


class Plotter:
    @classmethod
    def plot(cls, plots):
        cls.makedirs()
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
        plt.show()
        fig.savefig("images/fig.png") 

    @classmethod
    def plot_subplot(cls, ax, s):
        # ax.scatter(0, 0, color='white') 
        ax.minorticks_on()
        ax.grid(True, which='major', linewidth=1)
        ax.grid(True, which='minor', linewidth=0.5)
        ax.set_xlabel(s.axes_labels[0] + ', ' + s.axes_pupils[0], fontsize=15)
        ax.set_ylabel(s.axes_labels[1] + ', ' + s.axes_pupils[1], fontsize=15)

        fx, fy = s.func_x, s.func_y
        gx = Gradient(fx.func_nm, fx.expr, fx.variables + ' ' + fx.constants, fx.points.shape[1])
        gy = Gradient(fy.func_nm, fy.expr, fy.variables + ' ' + fy.constants, fy.points.shape[1])
        gx.latex_derivatives()
        gy.latex_derivatives()
        s.x = fx.func_eval
        s.y = fy.func_eval
        s.xerr = gx.sigma_f(fx.constants_eval, fx.points, fx.variable_errors)
        s.yerr = gy.sigma_f(fy.constants_eval, fy.points, fy.variable_errors)
        order = np.argsort(s.x)
        s.x = s.x[order]
        s.y = s.y[order]
        s.xerr = s.xerr[order]
        s.yerr = s.yerr[order]
        r = np.linspace(0, 1.2 * s.x[len(s.x) - 1]) if s.x[0] > 0 else np.linspace(1.2 * s.x[0],
                                                                                   1.2 * s.x[len(s.x) - 1])

        f = open("generated_files/coefs.txt", 'a')
        if s.type == 'lsq':
            matrix = np.vstack([s.x, np.ones(len(s.y))]).T
            k, b = np.linalg.lstsq(matrix, s.y, rcond=None)[0]
            sigma_k, sigma_b = Plotter.sigma_eval(s.x, s.y, k, b) 
            f.write("lsq" + ' ' + s.color + ': k=' + str(k) + ' b='+str(b) +
                    ' sigma_k='+str(sigma_k)+' sigma_b='+str(sigma_b)+'\n\n')
            ax.plot(r, k*r+b, color=s.color, label=s.description, linewidth=1)
            ax.errorbar(s.x, s.y, s.yerr, s.xerr, fmt='o', markersize=3, linewidth=1,
                        color=s.color, ecolor='black', capsize=0)
        
        elif s.type == 'log':
            x = np.log(s.x)
            y = np.log(s.y)
            v = np.linspace(0, 1.2*x[len(x)-1])
            matrix = np.vstack([x, np.ones(len(y))]).T
            k, b = np.linalg.lstsq(matrix, y, rcond=None)[0]
            sigma_k, sigma_b = Plotter.sigma_eval(x, y, k, b) 
            f.write("lsq" + ' ' + s.color + ': k=' + str(k) + ' b='+str(b) + ' sigma_k='+str(sigma_k) +
                    ' sigma_b=' + str(sigma_b)+'\n\n')
            ax.plot(v, k*v+b, color=s.color, label=s.description, linewidth=1) 
            ax.errorbar(x, y, fmt='o', markersize=3, linewidth=1, color=s.color, ecolor='black', capsize=0)

        elif s.type.rstrip('_0123456789') == 'poly':
            coefs = np.polyfit(s.x, s.y, int(s.type.split('_')[1]))
            ys = np.zeros(len(r))
            for i, c in enumerate(coefs):
                ys += c * r ** (len(coefs)-i-1) 
            f.write("lsq" + ' ' + s.color + ":\n")
            for i, c in enumerate(coefs):
                f.write("a_"+str(len(coefs)-i-1) + "=" + str(c) + '\n')
            f.write('\n')
            ax.plot(r, ys, color=s.color, label=s.description, linewidth=1)
            ax.errorbar(s.x, s.y, s.yerr, s.xerr, fmt='o', markersize=3, linewidth=1, color=s.color,
                        ecolor='black', capsize=0)
        elif s.type == 'dots':
            ax.errorbar(s.x, s.y, s.yerr, s.xerr, fmt='o', markersize=3, linewidth=1, color=s.color,
                        ecolor='black', capsize=0)
            ax.scatter(s.x, s.y, color=s.color, label=s.description)
        ax.legend() 
        f.close()
    
    @staticmethod 
    def makedirs():
        if not os.path.exists('generated_files'):
            os.mkdir('generated_files')
        fopen = open("generated_files/coefs.txt", 'a')
        fopen.write('-----------------------------------------------------\n\n')
        if not os.path.isdir('images'):
            os.mkdir('images')
    
    @classmethod
    def sigma_eval(cls, x, y, k, b):
        xdisp = np.var(x)
        ydisp = np.var(y)
        sigma_k = np.sqrt((ydisp/xdisp - k ** 2) / (len(x)-2))
        sigma_b = sigma_k * np.sqrt(np.average(x * x))
        return sigma_k, sigma_b
