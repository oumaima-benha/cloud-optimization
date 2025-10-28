import matplotlib.pyplot as plt
import seaborn as sns

def plot_comparison_cout(df):
    """
    Visualise la comparaison des coûts
    """
    fig, ax1 = plt.subplots(figsize=(8, 4))
    sns.barplot(x="algorithme", y="coût_total", data=df, ax=ax1, palette="viridis")
    ax1.set_title("Comparaison du coût total par algorithme")
    ax1.set_ylabel("Coût total")
    ax1.set_xlabel("Algorithme")
    plt.tight_layout()
    plt.show()



def plot_comparison_temps(df):
    """
    Visualise la comparaison des temps d'exécution
    """
    fig, ax1 = plt.subplots(figsize=(8, 4))
    sns.barplot(x="algorithme", y="temps_exécution", data=df, ax=ax1, palette="viridis")
    ax1.set_title("Comparaison des temps d'exécution par algorithme")
    ax1.set_ylabel("Temps d'exécution")
    ax1.set_xlabel("Algorithme")
    plt.tight_layout()
    plt.show()