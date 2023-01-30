from pyomo.environ import *
from pyomo.opt import SolverFactory

Model = ConcreteModel(name="Sample", doc="sample model for using scip") # name doc は省略可

Model.y = Var(range(8), within=NonNegativeIntegers)

Model.x = Var(["AB", "CB", "WE"], within=NonNegativeIntegers)
# Model.x["AB"] = Model.y
v = {1:2, 2:1, 3:1}
Model.c = Param(range(1,4), initialize=v)

# Model.x1 = Var(within=NonNegativeIntegers)
# Model.x2 = Var(within=NonNegativeIntegers)
# Model.x3 = Var(within=NonNegativeIntegers)
# Model.x1 = Var(within=NonPositiveIntegers)
# Model.x2 = Var(within=NonPositiveIntegers)
# Model.x3 = Var(within=NonPositiveIntegers)


key_list = ["AB", "CB", "WE"]

def const_1(model):
    # return Model.c[1] * Model.x["AB"] + Model.c[2] * Model.x["CB"] + Model.c[3] * Model.x["WE"] <= 60
    return sum(model.x[i] for i in key_list)  + sum(model.x[i] for i in key_list) <= 60


# def const_2(model):
#     return Model.x[1] + 2 * Model.x[2] + Model.x[3] <= 60


# def const_3(model):
#     return Model.x[3] <= 30


Model.const_1 = Constraint(rule=const_1)
# Model.const_2 = Constraint(rule=const_2)
# Model.const_3 = Constraint(rule=const_3)


def objective(model):
    return 15 * Model.x["AB"] + 18 * Model.x["CB"] + 30 * Model.x["WE"]


Model.value = Objective(rule=objective, sense=maximize)

# opt = SolverFactory("scipampl")
opt = SolverFactory("scip") # solver を scip に変更 (scipamplでは動作しなかった)
result = opt.solve(Model, tee=True)
Model.display()
print('result: \n', result)

print('variables:')
print('    objective:', Model.value())
print('    x1:', Model.x["AB"]())
print('    x2:', Model.x["CB"]())
print('    x3:', Model.x["WE"]())



