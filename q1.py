import numpy as np
import streamlit as st
import pandas as pd

# ---------------- Parameters ----------------
POPULATION_SIZE = 300
CHROMOSOME_LENGTH = 80
GENERATIONS = 50
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.01
ELITISM = 2
TOURNAMENT_K = 3
SEED = 42

rng = np.random.default_rng(SEED)


def fitness(individual):
    return np.sum(individual)  # OneMax

def init_population():
    return rng.integers(0, 2, size=(POPULATION_SIZE, CHROMOSOME_LENGTH))

def tournament_selection(pop, fit):
    idx = rng.choice(len(pop), TOURNAMENT_K)
    return pop[idx[np.argmax(fit[idx])]]

def crossover(p1, p2):
    if rng.random() < CROSSOVER_RATE:
        point = rng.integers(1, CHROMOSOME_LENGTH)
        return (
            np.concatenate([p1[:point], p2[point:]]),
            np.concatenate([p2[:point], p1[point:]])
        )
    return p1.copy(), p2.copy()

def mutation(child):
    mask = rng.random(CHROMOSOME_LENGTH) < MUTATION_RATE
    child[mask] = 1 - child[mask]
    return child


def run_ga():
    pop = init_population()
    history = []

    for gen in range(GENERATIONS):
        fit = np.array([fitness(ind) for ind in pop])

        history.append({
            "Generation": gen + 1,
            "Best Fitness": fit.max(),
            "Average Fitness": fit.mean()
        })

        # Elitism
        elite_idx = np.argsort(fit)[-ELITISM:]
        elites = pop[elite_idx]

        new_pop = []

        while len(new_pop) < POPULATION_SIZE - ELITISM:
            p1 = tournament_selection(pop, fit)
            p2 = tournament_selection(pop, fit)
            c1, c2 = crossover(p1, p2)
            new_pop.append(mutation(c1))
            if len(new_pop) < POPULATION_SIZE - ELITISM:
                new_pop.append(mutation(c2))

        pop = np.vstack([new_pop, elites])

    final_fit = np.array([fitness(ind) for ind in pop])
    best = pop[np.argmax(final_fit)]

    return pd.DataFrame(history), best, final_fit.max()


st.set_page_config(page_title="Genetic Algorithm – OneMax", layout="wide")
st.title("Genetic Algorithm")

if st.button("Run Genetic Algorithm"):
    history, best_solution, best_fitness = run_ga()

    st.subheader("Fitness Convergence")
    st.line_chart(history.set_index("Generation"))

    st.subheader("Best Solution Found")
    st.write(f"Best Fitness: **{best_fitness} / {CHROMOSOME_LENGTH}**")
    st.code("".join(best_solution.astype(str)))
