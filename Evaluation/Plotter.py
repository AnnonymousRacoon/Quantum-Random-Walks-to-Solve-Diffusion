from matplotlib import pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

def plot_distribution2D(results,n_qubits,savepath,title = None):
    """plots diffusion for 2D data"""
    
    x,y,alpha = results["dimension_0"],results["dimension_1"],results["probability_density"]
    axes_limit = (2**n_qubits)-1
    if title is None:
        title = "diffusion on an {}x{} grid".format(axes_limit+1,axes_limit+1)
    plt.scatter(x,y,alpha=[i**(1/4) for i in alpha],linewidths=[20*i**0.5 for i in alpha], s = [400*i**0.5 for i in alpha])
    plt.xlim(0,axes_limit)
    plt.ylim(0,axes_limit)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(title)
    plt.savefig(savepath,dpi = 300)
    plt.cla()