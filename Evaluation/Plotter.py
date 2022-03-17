from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import seaborn as sns
import sys

sns.set_style("whitegrid")

def plot_distribution1D(results,n_qubits,savepath,title = None):
    """plots diffusion for 1D data"""

    x,probability_density = results["dimension_0"],results["probability_density"]
    axes_limit = (2**n_qubits)-1
    if title is None:
        title = "diffusion on an {0} digit line".format(axes_limit+1)

    coords = [(i,j) for i,j in zip(x,probability_density)]
    coords.sort(key=lambda coord: coord[0])
    x_sorted = [coord[0] for coord in coords]
    probability_sorted = [coord[1] for coord in coords]

    plt.cla()
    plt.plot(x_sorted,probability_sorted,'o--')
    plt.xlim(0,axes_limit)
    plt.xlabel('X')
    plt.ylabel('Probability Density')
    plt.title(title)
    plt.savefig(savepath,dpi = 300)
    plt.cla()

def plot_distribution2D(results,n_qubits,savepath,title = None):
    """plots diffusion for 2D data"""

    x,y,probability_density = results["dimension_0"],results["dimension_1"],results["probability_density"]
    axes_limit = (2**n_qubits)-1
    if title is None:
        title = "diffusion on an {0}x{0} grid".format(axes_limit+1)

    if sys.version_info >= (3, 7):
        alpha = [i**(1/4) for i in probability_density]
    else:
        alpha = None
    plt.cla()
    plt.scatter(x,y,alpha=alpha,linewidths=[20*i**0.5 for i in probability_density], s = [400*i**0.5 for i in probability_density])
    plt.xlim(0,axes_limit)
    plt.ylim(0,axes_limit)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(title)
    plt.savefig(savepath,dpi = 300)
    plt.cla()


def plot_distribution3D(results,n_qubits,savepath,title = None):
    """plots diffusion for 3D data"""
    
    x,y,z,probability_density = results["dimension_0"],results["dimension_1"],results["dimension_2"],results["probability_density"]
    axes_limit = (2**n_qubits)-1
    if title is None:
        title = "diffusion on an {0}x{0}x{0} grid".format(axes_limit+1)
    
    if sys.version_info >= (3, 7):
        alpha = [i**(1/4) for i in probability_density]
    else:
        alpha = None

    plt.cla()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z,alpha=alpha, s = [400*i**0.5 for i in probability_density])
    ax.set_xlim(0, axes_limit)
    ax.set_ylim(0, axes_limit)
    ax.set_zlim(0, axes_limit)
    plt.xlim(0,axes_limit)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    plt.savefig(savepath,dpi = 300)
    plt.cla()