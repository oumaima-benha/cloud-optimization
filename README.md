# Cloud Service Placement Optimization Project  

## Introduction  

Ce projet a pour objectif de modéliser et d’optimiser le **placement de services cloud** dans un ensemble de régions, machines et infrastructures hétérogènes, en respectant un ensemble de **contraintes de disponibilité, sécurité, performance et conformité géographique**.  

L’enjeu est d’attribuer, pour chaque service, un **type de machine** et une **région de déploiement**, de façon à **minimiser le coût global** tout en garantissant un **niveau de conformité et de performance acceptable**.  

Le projet simule le comportement de plateformes cloud (type AWS, Azure, GCP) et implémente plusieurs approches d’optimisation pour comparer leurs performances.  

---

## Type de problème

Le problème de placement des services cloud appartient à la famille des **problèmes d’optimisation combinatoire**.  

Plus précisément, il s’agit d’un **problème d’affectation multi-dimensionnel avec contraintes multiples**, proche du **problème NP-difficile**.  

### Justification :
- Chaque service doit être affecté à **une machine et une région** parmi un ensemble fini → combinatoire.  
- Les contraintes de capacité, sécurité et latence rendent la recherche d’une solution **non triviale**.  
- La fonction d’évaluation inclut plusieurs composantes parfois conflictuelles (coût ↔ performance ↔ conformité).  
- Les solutions exactes (programmation linéaire ou MILP) deviennent inexploitables pour des instances moyennes → **recours à des heuristiques et métaheuristiques**.  

---

## Objectifs pédagogiques et techniques  

- Construire un **modèle de données cohérent** (services, régions, flux, machines, contraintes).  
- Définir une **fonction d’évaluation** (coûts, SLA, sécurité, conformité).  
- Générer des **instances aléatoires réalistes** de déploiement.  
- Implémenter et comparer plusieurs **algorithmes d’optimisation**. 
- Mesurer les **performances et la convergence** de chaque méthode.  
- Effectuer des **tests unitaires** pour valider les fonctions critiques.  

---

## Architecture du projet  

```
project_root/
│
├── algorithms/
│   ├── greedy.py
│   ├── simulated_annealing.py
│   ├── genetic.py
│
├── utils/
│   ├── data_model.py
│   ├── evaluate.py
│   ├── generate_instances.py
│   ├── print_solution.py
│   ├── random_solution_generator.py
│   ├── run_experiment.py
│   ├── visualization.py
│
├── tests/
│   ├── test_data_model.py
│   ├── test_evaluate.py
│   ├── test_generate_instances.py
│   ├── test_greedy.py
│   ├── test_simulated_annealing.py
│   ├── test_genetic.py
│
├── instances/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation  

### 1️ Cloner le projet  

```bash
git clone https://github.com/oumaima-benha/cloud-optimization
cd cloud-optimization
```

### 2️ Créer un environnement virtuel  

```bash
python -m venv venv
source venv/bin/activate  # sous Linux/Mac
venv\Scripts\activate     # sous Windows
```

### 3️ Installer les dépendances  

```bash
pip install -r requirements.txt
```

---

## Phase 1 – Modélisation  

Avant la phase de codage, une **modélisation mathématique manuelle** du problème a été réalisée afin de clarifier les variables, contraintes et fonctions de coût.

📎 [Voir le document PDF de modélisation](modélisation.pdf)

Ce document contient :
- Une **formulation en variables de décision** :  
  - `x_{s,m,r} = 1` si le service *s* est placé sur la machine *m* dans la région *r*, sinon `0`.  
  - `enc_{i,j} = 1` si le flux entre les services *i* et *j* est chiffré, sinon `0`.
- Les **contraintes principales** :  
  - Capacité CPU, mémoire, stockage, bande passante.  
  - Contraintes de sécurité et de zones.  
  - Contraintes de latence et de disponibilité.  
  - Contraintes géographiques (régions autorisées).  
- La **fonction objectif** :  
  Minimiser la somme pondérée des coûts de machine, stockage, réseau, sécurité, conformité, etc.

L’objectif de cette modélisation était de fournir une base claire et rigoureuse avant le développement des algorithmes de solution.  


Le cœur du projet repose sur un modèle de données clair défini dans `data_model.py`.

### 🧩 Entités principales :

| Entité | Description |
|--------|--------------|
| **Service** | Unité de déploiement avec CPU, mémoire, stockage, SLA, zone de sécurité. |
| **MachineType** | Machine disponible (petite, moyenne, grande). |
| **Region** | Localisation géographique (r1, r2, etc.). |
| **Flow** | Flux réseau entre deux services (bande passante, latence, chiffrement). |
| **Instance** | Conteneur regroupant tous les services, machines, régions et flux (un problème à résoudre). |
| **Placement** | Solution de déploiement (service → machine, région, redondance, chiffrement). |

---

## Phase 2 – Fonction d’évaluation  

La fonction `evaluate(instance, placement)` calcule le **coût total d’une solution** en additionnant plusieurs sous-coûts :

| Composant | Fonction | Type de contrainte | Description |
|------------|-----------|--------------------|--------------|
| Coût machine | `cost_machine()` | Dure | Machine non dispo ou redondance non supportée |
| Coût stockage | `cost_storage()` | Souple | Pénalité si service non placé |
| Réseau | `cost_network()` | Dure | Si lien réseau impossible (math.inf), la fonction s’arrête. |
| Sécurité | `cost_security_violation()` | Dure/Souple | Si communication interdite sinon pénalisée (souple) |
| Chiffrement | `cost_encryption_violation()` | Souple | Si chiffrement manquant alors que requis → pénalité |
| Performance | `cost_network_performance_violation()` | Souple | Si latence max dépassée → pénalité (latence > limite), mais pas infaisable |
| SLA | `cost_availability()` | Dure/Souple | Si SLA impossible (math.inf) → dure ; sinon coût progressif selon SLA |
| Capacité | `cost_capacity_violation()` | Dure/Souple | Si dépassement critique → math.inf, sinon pénalité modérée. |
| Cybersécurité | `cost_cybersecurity()` | Souple | Score de risque global |
| Géographie | `cost_geography_violation()` | Dure/Souple | Si région interdite → math.inf ; sinon pénalité pour non-conformité (RGPD, souveraineté) |

Toute contrainte “dure” entraîne `math.inf` → solution infaisable.

---

## Phase 3 – Structure Python du projet  

Chaque module a une responsabilité unique :
- `data_model.py` : structures de données
- `evaluate.py` : fonction d’évaluation globale
- `generate_instances.py` : génération aléatoire d’instances de test
- `print_solution.py` : affichage formaté d’un placement
- `run_experiment.py` : exécution d’un algorithme et mesure de son coût
- `visualization.py` : graphiques et comparaisons

---

## Phase 4 – Génération des données  

Le script `generate_instances.py` crée des **instances réalistes et aléatoires** :
- services avec besoins CPU/Mem aléatoires,  
- régions avec latences et coûts variables,  
- flux inter-services avec bande passante et exigences de sécurité,  
- stockage des instances en `.json` dans le dossier `instances/`.

Exemple :
```python
instance = generate_instance(nb_services=5, nb_regions=3, nb_machines=2)
```

---

## Phase 5 – Algorithmes d’optimisation  
### 1️ Algorithme Greedy (glouton)

#### Justification du choix
Le greedy a été choisi comme **approche initiale simple et rapide**.  
Il fournit une base de référence raisonnable et permet de vérifier la cohérence du modèle.  
Bien qu’il puisse rester bloqué dans un minimum local, il donne souvent une solution correcte en un temps minimal.

#### Description et pseudo-code

```text
Entrée : instance (services, machines, regions, flows, règles...), evaluate(instance, placement)
Sortie : placement_greedy

Algorithme GreedyPlacement :
  placement <- placement vide
  encryption defaults <- {}
  ordem_services <- liste des services triée par importance décroissante (ex : cpu décroissant)

  Pour chaque service s dans ordem_services :
    best_cost <- +∞
    best_assignment <- None

    Pour chaque machine_type m dans instance.machines :
      Pour chaque region r dans s.allowed_regions :
        # tentative : placer s sur (m,r)
        placement_temp <- copie profonde de placement
        placement_temp.placement[s] <- (m, r)
        placement_temp.redundancy[s] <- 1  # par défaut (on pourrait essayer >1)
        # mettre à jour chiffrement des flux impliquant s : si nécessaire utiliser f.encryption_required
        pour chaque flux f qui implique s :
          if f.src ou f.dst déjà placé dans placement_temp :
            placement_temp.encryption[(f.src,f.dst)] <- f.encryption_required

        (cost, details) <- evaluate(instance, placement_temp)

        Si cost < best_cost :
          best_cost <- cost
          best_assignment <- (m, r)

    Si best_assignment est non None et best_cost < +∞ :
      placer s dans placement en utilisant best_assignment
    Sinon :
      laisser s non placé (ou marquer comme impossible)

  Retourner placement
```

Complexité : **O(n × m × r x e)**  
(n = services, m = machines, r = régions, e = complexité de l'appel evaluate)

Si e ~ O(n + f), on obtient : **O(n × m × r x (n + f))** 

---

### 2️ Algorithme du Recuit Simulé (Simulated Annealing)

#### Justification du choix
Le recuit simulé a été choisi car il permet d’explorer l’espace de recherche **au-delà des minima locaux**, en introduisant une notion de **température** qui diminue progressivement.  
Il est particulièrement adapté aux problèmes combinatoires avec plusieurs contraintes douces.

#### Description et pseudo-code

```text
Entrée : instance, evaluate, placement_initial (optionnel)
Paramètres : T0 (température initiale), Tmin (température finale), alpha (facteur de refroidissement),
             iter_per_T (itérations par palier de température), max_eval (optionnel)

Si placement_initial est None :
  placement_current <- solution aléatoire ou greedy(instance)
Sinon :
  placement_current <- placement_initial

cost_current <- evaluate(instance, placement_current)

placement_best <- copie(placement_current)
cost_best <- cost_current

T <- T0
while T > Tmin and nombre_evaluations < max_eval :
  for i in 1..iter_per_T :
    neighbor <- générer_voisin(placement_current, instance)
      # voisin = déplacer un service vers une autre (machine, région)
      # ou toggler chiffrement pour un flux, ou changer redondance
    cost_neighbor <- evaluate(instance, neighbor)

    delta = cost_neighbor - cost_current

    if cost_neighbor < cost_current :
      # toujours accepter amélioration
      placement_current <- neighbor
      cost_current <- cost_neighbor
      if cost_neighbor < cost_best :
        placement_best <- copie(neighbor)
        cost_best <- cost_neighbor
    else :
      # accepter avec probabilité exp(-delta / T)
      prob = exp(-delta / T)
      if random() < prob :
        placement_current <- neighbor
        cost_current <- cost_neighbor

  T <- T * alpha  # refroidissement

Retourner placement_best

```

Complexité : **O(k × n)**  
(k = nombre d’itérations, n = services)

---

### 3️ Algorithme Génétique (Genetic Algorithm)

#### Justification du choix
Les algorithmes génétiques permettent une **exploration globale** de l’espace de solutions grâce à la combinaison (croisement) et à la mutation de plusieurs individus.  
Ils sont efficaces pour les problèmes de grande dimension et multi-critères.

#### Description et pseudo-code

```text
Entrée : instance, evaluate
Paramètres : pop_size, generations, elite_count, mutation_rate

Fonction GeneticAlgorithm(instance):
  # 1. Initialisation : créer une population d'individus (placements) aléatoires
  population <- [random_individual(instance) for i in 1..pop_size]
  évaluer chaque individu -> fitness = cost (plus petit = meilleur)

  Pour g de 1 à generations :
    # 2. Sélection : garder les meilleurs (élitisme) + sélectionner parents pour reproduction
    trier population par fitness croissante
    new_population <- meilleurs elite_count individus (é élite)

    # 3. Reproduction : produire des enfants jusqu'à pop_size
    tant que len(new_population) < pop_size :
      parent1 <- sélection(parent pool)   # ex : tournoi
      parent2 <- sélection(parent pool)
      enfant <- crossover(parent1, parent2)
      mutate(enfant) avec probabilité mutation_rate
      ajouter enfant à new_population

    population <- new_population
    évaluer population (fitness)
    mettre à jour best global si trouvé amélioration

  Retourner meilleur individu (placement) et son coût
```

Complexité : **O(pop × gen × e)**  
(pop = taille de la population, gen = nb de générations, e = evaluate)

---

## Phase 6 – Comparaison et visualisation  

###  Objectif  
Comparer la performance des algorithmes sur une même instance :  
- coût final,  
- temps d’exécution,  

### 📁 `utils/run_experiment.py`
Exécute un algorithme, mesure le temps et renvoie un dictionnaire de résultats uniformes.  

### 📁 `utils/visualization.py`
- `plot_comparison_cout(df)` → barplot comparatif des coûts.  
- `plot_comparison_temps(df)` → barplot comparatif des temps d'exécuttion. 

---

## Phase 7 – Tests unitaires  

Les tests sont dans `tests/` et vérifient :
- la structure des données (`test_data_model.py`),
- la cohérence des coûts (`test_evaluate.py`),
- la génération d’instances (`test_generate_instances.py`),
- la validité des solutions (`test_greedy.py`, `test_simulated_annealing.py`, `test_genetic.py`).

Exécution :
```bash
python -m pytest -v
```

Exemple de sortie :
```
collected 7 items

tests/test_data_model.py::test_service_creation PASSED                     [ 14%]
tests/test_data_model.py::test_instance_structure PASSED                   [ 28%]
tests/test_evaluate.py::test_evaluate_simple_case PASSED                   [ 42%]
tests/test_generate_instances.py::test_generate_instance_structure PASSED  [ 57%]
tests/test_genetic.py::test_genetic_algorithm_valid_result PASSED          [ 71%]
tests/test_greedy.py::test_greedy_valid_solution PASSED                    [ 85%]
tests/test_simulated_annealing.py::test_simulated_annealing_runs PASSED    [100%]

=================================== 7 passed in 0.16s ===================================
```

---

## Phase 8 – Résultats et comparaison

## 📈 Résultats expérimentaux 
Pour une instance : nb_services=300, nb_regions=140, nb_machines=150

| Algorithme | Coût total | Temps (s) |
|-------------|-------------|-----------|
| Baseline aléatoire | 284491.504587 | 0.000 |
| Greedy | 263399.268650 | 57.816 |
| Recuit simulé | 129678.486697 | 60.909 |
| Algorithme génétique | 205734.048572 | 1.342 |


![Comparaison des coûts](/results/Figure_1_nb_services=300_nb_regions=140_nb_machines=150.png)
![Comparaison du temps d'exéc](/results/Figure_2_nb_services=300_nb_regions=140_nb_machines=150.png)

---
Et pour une instance : nb_services=500, nb_regions=120, nb_machines=200

| Algorithme | Coût total | Temps (s) |
|-------------|-------------|-----------|
| Baseline aléatoire | 464363.203794 | 0.001 |
| Greedy | 432593.335044 | 145.671 |
| Recuit simulé | 269491.114653 | 167.845 |
| Algorithme génétique | 371297.544809 | 2.599 |

![Comparaison des coûts](/results/Figure_1_nb_services=500_nb_regions=120_nb_machines=200.png)
![Comparaison du temps d'exéc](/results/Figure_2_nb_services=500_nb_regions=120_nb_machines=200.png)
---
## 📈 Analyse des résultats
La première remarque essentielle est qu’il est nécessaire de remplacer les fonctions « boîtes noires » utilisées pour le calcul des coûts par leurs véritables implémentations, afin d’obtenir une estimation plus réaliste des coûts partiels et du coût total. En effet, dans la version actuelle, ces fonctions ne sont que des placeholders permettant simplement d’exécuter et de tester les algorithmes, ce qui ne fournit pas des valeurs de coûts exactes.

Par conséquent, les résultats présentés ne constituent qu’un aperçu approximatif de ce que l’on pourrait obtenir, sans pour autant refléter fidèlement les différences réelles entre les coûts issus des solutions de chaque algorithme.

Néanmoisn, les résultats montrent une amélioration nette du coût total avec les méthodes stochastiques.

## Analyse du temps d'exécution
En ce qui concerne le temps d’exécution, on peut observer que les algorithmes Greedy et Recuit simulé nécessitent un temps de calcul plus important, d’environ 2 à 3 minutes pour le traitement de 500 à 1000 services à affecter.
En revanche, l’algorithme génétique est nettement plus rapide, avec un temps d’exécution de seulement 2 à 3 secondes, tout en produisant des résultats de coût proches de ceux obtenus par le Recuit simulé.

Cette différence de performance s’explique par la complexité algorithmique propre à chaque méthode. Le Recuit simulé repose sur un processus itératif de recherche locale nécessitant de nombreuses évaluations successives de solutions, tandis que l’algorithme génétique exploite la recombinaison de solutions au sein d’une population, ce qui permet d’explorer efficacement l’espace de recherche tout en limitant le nombre total d’itérations. Quant à la méthode Greedy, bien que simple dans son principe, elle peut devenir coûteuse lorsqu’elle doit évaluer plusieurs choix possibles à chaque étape pour de grandes instances du problème.

---

## Phase 9 – Analyse de sensibilité des paramètres

## Recuit simulé (Simulated Annealing)

### **Figure 1 – Heatmap : Influence de T₀ et α sur le coût moyen**
![Heatmap Recuit Simulé](/results/Figure_1.png)
La première figure illustre la variation du coût moyen obtenu en fonction de la **température initiale (T₀)** et du **facteur de refroidissement (α)**.  
On observe que :
- Une **température initiale trop basse (T₀ = 500)** donne souvent des coûts élevés : l’algorithme explore moins bien l’espace de recherche et risque de rester bloqué dans un minimum local.  
- Une **valeur intermédiaire ou élevée de T₀ (1000–2000)** combinée à un **facteur α ≈ 0.85–0.9** donne les **meilleurs compromis coût/temps**.  
- Des valeurs de α trop faibles (0.8) refroidissent trop rapidement le système, limitant l’exploration et dégradant la qualité des solutions.

✅ **Conclusion :**
Le recuit simulé est sensible au couple *(T₀, α)*.  
Un bon équilibre entre exploration et exploitation se situe typiquement autour de :
```
T₀ ≈ 1000 – 2000
α ≈ 0.85 – 0.9
```
Ces paramètres permettent une convergence plus douce et un coût moyen minimal.

---

### **Figure 2 – Évolution du coût moyen en fonction de T₀**
![Évolution du coût moyen en fonction de T₀](/results/Figure_2.png)

Cette courbe confirme la tendance précédente :  
le coût moyen décroît nettement lorsque T₀ augmente de 500 à 1000, puis se stabilise au-delà de 1000.  
Cela traduit une **amélioration initiale grâce à une exploration plus large**, suivie d’un **rendement marginal décroissant** quand la température devient trop haute.

---

## Algorithme génétique (Genetic Algorithm)

### **Figure 3 – Heatmap : Influence de la taille de population et du taux de mutation**
![Heatmap GA](/results/Figure_1_GA.png)
La heatmap met en évidence deux observations :
- Une **plus grande population (pop_size 20–30)** tend à améliorer la qualité du résultat (coût plus faible), car elle augmente la diversité génétique.  
- Un **taux de mutation modéré (0.1)** donne souvent les meilleurs résultats :  
  - Trop bas (0.05) → risque de stagnation prématurée,  
  - Trop haut (0.2) → trop de perturbations, perte de convergence.  

✅ **Conclusion :**
Les meilleurs compromis sont atteints pour :
```
pop_size ≈ 20–30
mutation_rate ≈ 0.1
```
Le modèle est donc plus stable avec une diversité génétique modérée et un taux de mutation équilibré.

---

### **Figure 4 – Évolution du coût moyen selon la taille de la population**
![Évolution du coût moyen selon la taille de la population](/results/Figure_2_GA.png)

Cette courbe illustre une **tendance décroissante du coût moyen** quand la population augmente.  
Cela confirme que **plus de diversité dans la population initiale améliore la qualité moyenne des solutions**, bien que le temps de calcul augmente légèrement.

---

## 🧩 Interprétation globale

| Algorithme | Paramètres clés | Observation principale | Zone optimale |
|-------------|----------------|------------------------|----------------|
| Recuit simulé | T₀, α | Trop faible → minimum local ; trop élevé → convergence lente | T₀ = 1000–2000 ; α = 0.85–0.9 |
| Génétique | pop_size, mutation_rate | Trop faible → stagnation ; trop fort → instabilité | pop_size = 20–30 ; mutation_rate = 0.1 |

---

## 💬 Conclusion générale
- Le **recuit simulé** offre une convergence stable et rapide, mais dépend fortement du calibrage thermique.  
- L’**algorithme génétique** est plus robuste aux variations de paramètres, mais nécessite une population suffisante pour garantir la diversité.  
- Dans les deux cas, la sensibilité est modérée mais significative : un mauvais réglage peut multiplier le coût final par 1.3 à 1.5.  
Ces résultats montrent qu’une **phase de tuning automatique** pourrait encore améliorer la performance globale du système.
---
## ⚠️ Limites et perspectives  

Plusieurs améliorations sont envisageables :  

La première perspective et limite identifiée consiste à remplacer les fonctions « boîtes noires » utilisées pour le calcul des coûts par leurs véritables implémentations, afin d’obtenir une estimation plus réaliste des coûts partiels et du coût total. En effet, dans cette version, ces fonctions ne sont que des placeholders servant à exécuter et tester les algorithmes, ce qui ne permet pas d’obtenir des valeurs de coûts exactes.
### 🔹 Sur le modèle
- Intégrer des coûts **dynamiques** dépendant du trafic réel.  
- Ajouter des contraintes **d’énergie et d’empreinte carbone**.  
- Introduire la **migration de services** (placement dynamique dans le temps).  

### 🔹 Sur les algorithmes
- Combiner Greedy + Recuit simulé en **algorithme hybride**.  
- Tester d’autres métaheuristiques : **Tabu Search, Ant Colony, Particle Swarm Optimization**.  
- Ajouter un module de **parallélisation** des évaluations de coût.  


Ces perspectives ouvrent la voie à un système d’optimisation plus robuste, intelligent et réaliste pour la gestion du placement cloud.

---

## Comment exécuter le projet  

```bash
python main.py
```

✅ Ce script :
1. Génère une instance aléatoire,  
2. Exécute les 4 algorithmes,  
3. Compare les coûts et temps,  
4. Affiche les placements et les graphiques.  

---

## Outils et dépendances  

| Outil | Utilisation |
|-------|--------------|
| Python 3.10+ | Langage principal |
| Pandas, Numpy | Analyse et comparaison des résultats |
| Matplotlib, Seaborn | Visualisations |
| Pytest | Tests unitaires |
| GitHub | Versionnement et documentation |

---

## Auteur & crédits  

**Projet réalisé par :** *Oumaima Ben*  
Dans le cadre d’un projet d’optimisation et de modélisation cloud.  