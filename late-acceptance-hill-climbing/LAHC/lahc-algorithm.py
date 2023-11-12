import numpy as np
import random

def readFile(filename):
    with open(filename, "r") as file:
        n = int(file.readline())
        C = np.zeros((n, n, n-1))
        data = [list(map(float, line.split())) for line in file]
        for i, j, r, cost in data:
            C[int(i), int(j), int(r)] = cost
        # C = sorted(C, key=lambda x: x[2])
        return n, C 

def calculateCost(rounds_range, C, schedule):
    cost = 0
    for r in rounds_range:
        for i in range(int(n/2)):
            # Soma no custo final o valor do
            cost += C[schedule[r][i][0]][schedule[r][i][1]][r]

    return cost

def greedyAlgorithm(n, C):
    print('Iremos tentar rodar nosso algoritmo guloso...')
    schedule = []
    total_cost = []
    for r in range(n-1):
        game_cost = []
        matches_in_round = set()
        for i in range(n):
            for j in range(i+1, n):
                # Se os dois times não se enfrentaram anteriormente, coloca esse jogo como possível de acontecer
                if ([i,j] not in schedule):
                    game_cost.append((i, j, C[i][j][r]))
        # Sort por custo da partida (crescente)
        game_cost.sort(key=lambda x:x[2])
        while True:
            i, j, _ = game_cost.pop(0)
            # Se algum dos times i e j já jogaram nessa rodada, pula iteração
            if i in matches_in_round or j in matches_in_round:
                if(len(game_cost) == 0):
                    break
                continue
            # Senão
            else:
                matches_in_round.add(i)
                matches_in_round.add(j)
                schedule.append([i,j])
                total_cost.append(i)
                if(len(game_cost) == 0):
                    break
        # Se o número de partidas realizadas na rodada não bater, throw exception
        if(len(matches_in_round) < n):
            raise  ValueError("O algoritmo guloso não conseguiu completar a chamada")
        print(f'Rodada {r} jogarão {schedule}')
        
    return total_cost, schedule

# Construir função que gera entrada válida p/ problema
def fallbackAlgorithm(n, C):
    teams = [i for i in range(0, n)]
    random.shuffle(teams)
    schedule = []

    if n % 2 != 0:
        teams.append(None)
        n += 1

    rounds = n - 1

    for _ in range(rounds):
        round_matches = []
        for i in range(n // 2):
            if teams[i] is not None and teams[n - i - 1] is not None:
                round_matches.append((teams[i], teams[n - i - 1]))
        schedule.append(round_matches)
        teams.insert(1, teams.pop())

    cost = calculateCost(range(n-1), C, schedule)
    for i in range(n-1):
        print(f'Rodada {i} jogarão {schedule[i]}')
    print(f'Custo total inicial: {cost}')
    return [cost, schedule]

def getNeighbour(cost, schedule, n, C):
    rounds_exchanged = random.sample(range(n-1), 2)
    neighbour_schedule = schedule[:]
    neighbour_schedule[rounds_exchanged[0]], neighbour_schedule[rounds_exchanged[1]] = schedule[rounds_exchanged[1]], schedule[rounds_exchanged[0]]
    initial_round_cost = calculateCost(rounds_exchanged, C, schedule)
    neighbour_round_cost = calculateCost(rounds_exchanged, C, neighbour_schedule)
    cost = cost - initial_round_cost + neighbour_round_cost
    return [cost, neighbour_schedule]

def lateAcceptanceHillClimbing(list_size, n, C):
    max_iter = 1000000
    i = 0
    cond_parada = 0
    try:
        [total_cost, schedule] = (greedyAlgorithm(n, C))
    except ValueError:
        print("Exceção capturada. Tentando algoritmo alternativo...")
        [total_cost, schedule] = fallbackAlgorithm(n,C)
    sol_atual = total_cost
    best_solution = sol_atual
    f = list_size * [sol_atual]
    while(i < max_iter and cond_parada < 0.1 * max_iter):
        [cost_v, schedule_v] = getNeighbour(sol_atual, schedule, n, C)
        vizinho = cost_v
        # Se a solução atual não for atualizada depois de muito tempo, iremos encerrar o laço
        if(vizinho >= sol_atual):
            cond_parada += 1
        else: 
            cond_parada = 0
        if((vizinho < f[-1]) or (vizinho <= sol_atual)):
            sol_atual = vizinho
            schedule = schedule_v[:]
        if(sol_atual < f[-1]):
            f.pop()
            f.insert(0, sol_atual)
        if(sol_atual < best_solution):
            best_solution = sol_atual
        i = i + 1
    return best_solution

filename = input('Digite o nome do arquivo: ')
n, C = readFile(f'instancias-problema2/{filename}')

sol = lateAcceptanceHillClimbing(100, n, C)
print(f'Solução final encontrada: {sol}')