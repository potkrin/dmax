from pyomo.environ import *
from pyomo.opt import SolverFactory

Model = ConcreteModel(name="Sample", doc="sample model for using scip") # name doc は省略可

skill_list = ["AB", "CB", "WE"]

Model.I = RangeSet(0, 8)
Model.x = Var(skill_list, Model.I, within=NonNegativeIntegers)

print(Model.x)
# Model.x["AB"] = Model.y
# v = {1:2, 2:1, 3:1}
# Model.c = Param(range(1,4), initialize=v)


# key_list = ["AB", "CB", "WE"]

def const_1(model):
    # return Model.c[1] * Model.x["AB"] + Model.c[2] * Model.x["CB"] + Model.c[3] * Model.x["WE"] <= 60
    return sum(Model.x[j, i] for i in Model.I for j in skill_list) <= 60


Model.const_1 = Constraint(rule=const_1)


def objective(model):
    return 15 * Model.x["AB", 0] + 18 * Model.x["CB", 1] + 30 * Model.x["WE", 0]


Model.value = Objective(rule=objective, sense=maximize)

# opt = SolverFactory("scipampl")
opt = SolverFactory("scip") # solver を scip に変更 (scipamplでは動作しなかった)
result = opt.solve(Model, tee=True)
Model.display()
print('result: \n', result)

print('variables:')
print('    objective:', Model.value())
print('    x1:', Model.x["AB", 0]())
print('    x2:', Model.x["CB", 1]())
print('    x3:', Model.x["WE", 0]())







