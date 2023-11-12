from pyomo.environ import *
from pyomo.opt import SolverFactory
import time

def readFile(filename):
    with open(filename, 'r') as file:
        n = int(file.readline())
        data = [list(map(float, line.split())) for line in file] 
    return n, data

def main():
    filename = input('Digite o nome do arquivo: ')
    n, data = readFile(f'instancias-problema2/{filename}')

    model = ConcreteModel()

    # Indexes
    model.i = RangeSet(0, n-1)
    model.j = RangeSet(0, n-1)
    model.r = RangeSet(0, n-2)

    # Parameters
    model.c = Param(model.i, model.j, model.r, initialize=0, mutable=True)
    for i, j, r, cost in data:
        model.c[i, j, r] = cost

    # Variables
    model.x = Var(model.i, model.j, model.r, domain=Binary)
    model.y = Var(model.r, domain=NonNegativeReals, initialize=0)

     # Constraints
     # Garantir que cada time não jogue contra si mesmo
    def teamIDontPlayAgainstTeamI(model, i, r):
        return model.x[i,i,r] == 0
    model.Constraint1 = Constraint(model.i, model.r, rule=teamIDontPlayAgainstTeamI)

    # Como os jogos entre os times i e j são os mesmos que entre j e i, podemos estabelecer a simetria
    def simetryEstabilished(model, i, j, r):
        return model.x[i,j,r] == model.x[j,i,r]
    model.Constraint2 = Constraint(model.i, model.j, model.r, rule=simetryEstabilished)

    # Cada time joga exatamente uma vez em cada rodada
    def teamPlayOnceInRound(model, j, r):
        return sum(model.x[i,j,r] for i in model.i) == 1
    model.Constraint3 = Constraint(model.j, model.r, rule=teamPlayOnceInRound)

    def eachTeamPlaysAgaintsOneAnother(model, i, j):
        if i != j:
            return sum(model.x[i, j, r] for r in model.r) == 1
        else:
            return Constraint.Skip  # Pula a restrição quando i == j
    model.Constraint4 = Constraint(model.i, model.j, rule=eachTeamPlaysAgaintsOneAnother)

    # O custo total da rodada r é a soma dos custos dos jogos realizados naquela rodada
    def roundCostRule(model, r):
        return model.y[r] == (sum(sum(model.c[i, j, r] * model.x[i, j, r] for i in model.i) for j in model.j)) / 2
    model.Constraint5 = Constraint(model.r, rule=roundCostRule)

    # Objective
    model.obj = Objective(expr=sum(model.y[r] for r in model.r), sense=minimize)

    # model.pprint()
    start = time.time()
    solver = SolverFactory("glpk")
    solver.options['tmlim'] = 1800 # 30 minutos
    solution = solver.solve(model, logfile= "results.log")
    end = time.time()

    print("Status = ", solution.solver.status)
    print("Critério de parada = ", solution.solver.termination_condition)
    print("Custo = ", model.obj.expr())
    print(f"Completou processamento em {end - start} segundos")

main()