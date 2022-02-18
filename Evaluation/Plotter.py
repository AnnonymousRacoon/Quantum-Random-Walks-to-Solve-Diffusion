from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import seaborn as sns
sns.set_style("whitegrid")

def plot_distribution2D(results,n_qubits,savepath,title = None):
    """plots diffusion for 2D data"""

    x,y,alpha = results["dimension_0"],results["dimension_1"],results["probability_density"]
    axes_limit = (2**n_qubits)-1
    if title is None:
        title = "diffusion on an {0}x{0} grid".format(axes_limit+1)
    plt.scatter(x,y,alpha=[i**(1/4) for i in alpha],linewidths=[20*i**0.5 for i in alpha], s = [400*i**0.5 for i in alpha])
    plt.xlim(0,axes_limit)
    plt.ylim(0,axes_limit)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(title)
    plt.savefig(savepath,dpi = 300)
    plt.cla()


def plot_distribution3D(results,n_qubits,savepath,title = None):
    """plots diffusion for 3D data"""
    
    x,y,z,alpha = results["dimension_0"],results["dimension_1"],results["dimension_2"],results["probability_density"]
    axes_limit = (2**n_qubits)-1
    if title is None:
        title = "diffusion on an {0}x{0}x{0} grid".format(axes_limit+1)
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z,alpha=[i**(1/4) for i in alpha], s = [400*i**0.5 for i in alpha])
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