from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import seaborn as sns
import sys
import numpy as np

sns.set_style("whitegrid")

def plot_distribution1D(results,n_qubits,savepath,title = None, clear_fig = True):
    plt.rcParams.update({'figure.figsize': (10,10)})
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
    if clear_fig:
        plt.cla()

def plot_distribution2D(results,n_qubits,savepath,title = None, clear_fig = True):
    """plots diffusion for 2D data"""
    plt.rcParams.update({'figure.figsize': (10,10)})
    y,x,probability_density = results["dimension_0"],results["dimension_1"],results["probability_density"]
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
    if clear_fig:
        plt.cla()


def plot_distribution_2D_topological(results,n_qubits,savepath,title = None, clear_fig = True):
    plt.rcParams.update({'figure.figsize': (20,10)})
    plt.tight_layout(pad=0)
    x,y,probability_density = results["dimension_0"],results["dimension_1"],results["probability_density"]

    if type(n_qubits) == list:
        axes_limit = [(2**n)-1 for n in n_qubits]
    else:
        axes_limit = [(2**n_qubits)-1 for _ in range(2)]

    fig, ax = plt.subplots(1,2,subplot_kw={"projection": "3d"})
    plt.subplots_adjust(wspace=0)
    plt.subplots_adjust(hspace=0)

    # Make data.
    X = np.arange(0,axes_limit[0]+1, 1, dtype=float)
    Y = np.arange(0,axes_limit[1]+1, 1, dtype=float)
    X, Y = np.meshgrid(X, Y)
    Z = X*0

    for px,py,prob in zip(x,y,probability_density):
        Z[px][py] = prob


    plt.cla()

    for subplot_idx in range(2):
        # Plot the surface.
        surf = ax[subplot_idx].plot_surface(X, Y, Z, cmap=cm.viridis,
                            linewidth=0, antialiased=True)

        # Customize the z axis.
        # ax.set_zlim(0,1)
        ax[subplot_idx].zaxis.set_major_locator(LinearLocator(10))
        # A StrMethodFormatter is used automatically
        ax[subplot_idx].zaxis.set_major_formatter('{x:.02f}')
        ax[subplot_idx].set_xlabel('X')
        ax[subplot_idx].set_ylabel('Y')
        ax[subplot_idx].set_zlabel('Probability')
        ax[subplot_idx].set_title(title)

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)
    ax[0].view_init(azim=0, elev=90) 

   
    plt.savefig(savepath,dpi = 300)
    if clear_fig:
        plt.cla()
        plt.close()




def plot_distribution3D(results,n_qubits,savepath,title = None, clear_fig = True):
    """plots diffusion for 3D data"""
    plt.rcParams.update({'figure.figsize': (10,10)})
    z,y,x,probability_density = results["dimension_0"],results["dimension_1"],results["dimension_2"],results["probability_density"]
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
    if clear_fig:
        plt.cla()