import matplotlib.pyplot as plt
import seaborn as sns

def plot_cost_comparison(df):
    """
    Visualize the comparison of total costs
    """
    fig, ax1 = plt.subplots(figsize=(8, 4))
    sns.barplot(x="algorithm", y="total_cost", data=df, ax=ax1, palette="viridis")
    ax1.set_title("Comparison of Total Cost by Algorithm")
    ax1.set_ylabel("Total Cost")
    ax1.set_xlabel("Algorithm")
    plt.tight_layout()
    plt.show()


def plot_execution_time_comparison(df):
    """
    Visualize the comparison of execution times
    """
    fig, ax1 = plt.subplots(figsize=(8, 4))
    sns.barplot(x="algorithm", y="execution_time", data=df, ax=ax1, palette="viridis")
    ax1.set_title("Comparison of Execution Time by Algorithm")
    ax1.set_ylabel("Execution Time (s)")
    ax1.set_xlabel("Algorithm")
    plt.tight_layout()
    plt.show()