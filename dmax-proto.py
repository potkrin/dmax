# dmax の試作品
# 擬似的にスキルシミュによる制約を再現したもの
# ダメージ計算式が間違ってる (正しい式は damage_expression.py または dmax_skill_sim_scip.py を参照)
# 次に作成したのが dmax-proto-refact.py

# from pyomo.environ import *
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel(name="Sample", doc="sample model for using scip") # name doc は省略可


model.AB0 = pyo.Var(within=pyo.Boolean)
model.AB1 = pyo.Var(within=pyo.Boolean)
model.AB2 = pyo.Var(within=pyo.Boolean)
model.AB3 = pyo.Var(within=pyo.Boolean)
model.AB4 = pyo.Var(within=pyo.Boolean)
model.AB5 = pyo.Var(within=pyo.Boolean)
model.AB6 = pyo.Var(within=pyo.Boolean)
model.AB7 = pyo.Var(within=pyo.Boolean)

model.FUKUMA_AKA0 = pyo.Var(within=pyo.Boolean)
model.FUKUMA_AKA1 = pyo.Var(within=pyo.Boolean)
model.FUKUMA_AKA2 = pyo.Var(within=pyo.Boolean)
model.FUKUMA_AKA3 = pyo.Var(within=pyo.Boolean)
model.FUKUMA_AO0 = pyo.Var(within=pyo.Boolean)
model.FUKUMA_AO1 = pyo.Var(within=pyo.Boolean)
model.FUKUMA_AO2 = pyo.Var(within=pyo.Boolean)
model.FUKUMA_AO3 = pyo.Var(within=pyo.Boolean)

model.SAKAURAMI0 = pyo.Var(within=pyo.Boolean)
model.SAKAURAMI1 = pyo.Var(within=pyo.Boolean)
model.SAKAURAMI2 = pyo.Var(within=pyo.Boolean)
model.SAKAURAMI3 = pyo.Var(within=pyo.Boolean)
model.SAKAURAMI4 = pyo.Var(within=pyo.Boolean)
model.SAKAURAMI5 = pyo.Var(within=pyo.Boolean)

model.MIKIRI0 = pyo.Var(within=pyo.Boolean)
model.MIKIRI1 = pyo.Var(within=pyo.Boolean)
model.MIKIRI2 = pyo.Var(within=pyo.Boolean)
model.MIKIRI3 = pyo.Var(within=pyo.Boolean)
model.MIKIRI4 = pyo.Var(within=pyo.Boolean)
model.MIKIRI5 = pyo.Var(within=pyo.Boolean)
model.MIKIRI6 = pyo.Var(within=pyo.Boolean)
model.MIKIRI7 = pyo.Var(within=pyo.Boolean)

model.CHOUSENSHA0 = pyo.Var(within=pyo.Boolean)
model.CHOUSENSHA1 = pyo.Var(within=pyo.Boolean)
model.CHOUSENSHA2 = pyo.Var(within=pyo.Boolean)
model.CHOUSENSHA3 = pyo.Var(within=pyo.Boolean)
model.CHOUSENSHA4 = pyo.Var(within=pyo.Boolean)
model.CHOUSENSHA5 = pyo.Var(within=pyo.Boolean)

model.HUNTOU0 = pyo.Var(within=pyo.Boolean)
model.HUNTOU1 = pyo.Var(within=pyo.Boolean)
model.HUNTOU2 = pyo.Var(within=pyo.Boolean)
model.HUNTOU3 = pyo.Var(within=pyo.Boolean)
model.HUNTOU4 = pyo.Var(within=pyo.Boolean)
model.HUNTOU5 = pyo.Var(within=pyo.Boolean)

model.CHOUKAISIN0 = pyo.Var(within=pyo.Boolean)
model.CHOUKAISIN1 = pyo.Var(within=pyo.Boolean)
model.CHOUKAISIN2 = pyo.Var(within=pyo.Boolean)
model.CHOUKAISIN3 = pyo.Var(within=pyo.Boolean)









# model.x2 = pyo.Var(within=NonNegativeIntegers)
# model.x3 = pyo.Var(within=NonNegativeIntegers)
# model.x1 = pyo.Var(within=NonPositiveIntegers)
# model.x2 = pyo.Var(within=NonPositiveIntegers)
# model.x3 = pyo.Var(within=NonPositiveIntegers)



def const_AB(model):
    return 1 == model.AB0 + model.AB1 + model.AB2 + model.AB3 + model.AB4 + model.AB5 + model.AB6 + model.AB7

def const_FUKUMA(model):
    return 1 == model.FUKUMA_AKA0 + model.FUKUMA_AKA1 + model.FUKUMA_AKA2 + model.FUKUMA_AKA3 \
                + model.FUKUMA_AO0 + model.FUKUMA_AO1 + model.FUKUMA_AO2 + model.FUKUMA_AO3

def const_CHOUSENSHA(model):
    return 1 == model.CHOUSENSHA0 + model.CHOUSENSHA1 + model.CHOUSENSHA2 + model.CHOUSENSHA3 \
                + model.CHOUSENSHA4 + model.CHOUSENSHA5

def const_SAKAURAMI(model):
    return 1 == model.SAKAURAMI0 + model.SAKAURAMI1 + model.SAKAURAMI2 + model.SAKAURAMI3 \
                + model.SAKAURAMI4 + model.SAKAURAMI5

def const_MIKIRI(model):
    return 1 == model.MIKIRI0 + model.MIKIRI1 + model.MIKIRI2 + model.MIKIRI3 + model.MIKIRI4 \
                + model.MIKIRI5 + model.MIKIRI6 + model.MIKIRI7

def const_HUNTOU(model):
    return 1 == model.HUNTOU0 + model.HUNTOU1 + model.HUNTOU2 + model.HUNTOU3 

def const_CHOUKAISIN(model):
    return 1 == model.CHOUKAISIN0 + model.CHOUKAISIN1 + model.CHOUKAISIN2 + model.CHOUKAISIN3 

def const_SKILL_NUM(model):
    return 11 >= \
    1 * model.AB1 + 2 * model.AB2 + 3 * model.AB3 + 4 * model.AB4 + 5 * model.AB5 + 6 * model.AB6 + 7 * model.AB7 + \
    1 * model.FUKUMA_AKA1 + 2 * model.FUKUMA_AKA2 + 3 * model.FUKUMA_AKA3 + \
    1 * model.FUKUMA_AO1 + 2 * model.FUKUMA_AO2 + 3 * model.FUKUMA_AO3 + \
    1 * model.CHOUSENSHA1 + 2 * model.CHOUSENSHA2 + 3 * model.CHOUSENSHA3 +  \
    4 * model.CHOUSENSHA4 + 5 * model.CHOUSENSHA5 + \
    1 * model.SAKAURAMI1 + 2 * model.SAKAURAMI2 + 3 * model.SAKAURAMI3 +  \
    4 * model.SAKAURAMI4 + 5 * model.SAKAURAMI5 + \
    1 * model.MIKIRI1 + 2 * model.MIKIRI2 + 3 * model.MIKIRI3 + 4 * model.MIKIRI4 +  \
    5 * model.MIKIRI5 + 6 * model.MIKIRI6 + 7 * model.MIKIRI7 +  \
    1 * model.HUNTOU1 + 2 * model.HUNTOU2 + 3 * model.HUNTOU3 +  \
    1 * model.CHOUKAISIN1 + 2 * model.CHOUKAISIN2 + 3 * model.CHOUKAISIN3 


# def const_2(model):
#     return model.x2 <= 30


model.const_AB = pyo.Constraint(rule=const_AB)
model.const_FUKUMA= pyo.Constraint(rule=const_FUKUMA)
model.const_CHOUSENSHA = pyo.Constraint(rule=const_CHOUSENSHA)
model.const_SAKAURAMI = pyo.Constraint(rule=const_SAKAURAMI)
model.const_MIKIRI= pyo.Constraint(rule=const_MIKIRI)
model.const_HUNTOU = pyo.Constraint(rule=const_HUNTOU)
model.const_CHOUKAISIN = pyo.Constraint(rule=const_CHOUKAISIN)
model.const_SKILL_NUM = pyo.Constraint(rule=const_SKILL_NUM)


# ((武器倍率) * (攻撃スキル) + (攻撃スキル加算 + 伏魔響命青 + 逆恨み)) * (物理溜め補正)
#     * (モーション値 / 100) *(肉質/100) * (強撃ビン補正) *(1.0 - (会心補正 - 1.0)
#     * (武器会心率 + 見切り + 挑戦者 + 奮闘))

# none lenear problem
def objective(model):
    return (300 * (1.0 *(model.AB0 + model.AB1 + model.AB2 + model.AB3) + 1.05 * model.AB4 + 1.06 * model.AB5 + 1.08 * model.AB6 + 1.1 * model.AB7) + 3 * model.AB1 + 6 * model.AB2 + 9 * model.AB3 + 7 * model.AB4 + 8 * model.AB5 + 9 * model.AB6 + 10 * model.AB7 + 15 * model.FUKUMA_AO1 + 20 * model.FUKUMA_AO2 + 25 * model.FUKUMA_AO3 + 4 * model.CHOUSENSHA1 + 8 * model.CHOUSENSHA2 + 12 * model.CHOUSENSHA3 + 16 * model.CHOUSENSHA4 + 20 * model.CHOUSENSHA5 + 5 * model.SAKAURAMI1 + 10 * model.SAKAURAMI2 + 15 * model.SAKAURAMI3 + 20 * model.SAKAURAMI4 + 25 * model.SAKAURAMI5) * (1.35) * (44/100) * (55/100) * (1.35) * (1 + (1.25 * model.CHOUKAISIN0 + 1.30 * model.CHOUKAISIN1 + 1.35 * model.CHOUKAISIN2 + 1.4 * model.CHOUKAISIN3 -1.0) * ((0 + 5 * model.MIKIRI1 + 10 * model.MIKIRI2 + 15 * model.MIKIRI3 + 20 * model.MIKIRI4 + 25 * model.MIKIRI5 + 30 * model.MIKIRI6 + 40 * model.MIKIRI7 + 3 * model.CHOUSENSHA1 + 5 * model.CHOUSENSHA2 + 7 * model.CHOUSENSHA3 + 10 * model.CHOUSENSHA4 + 15 * model.CHOUSENSHA5 + 10 * model.HUNTOU1 + 15 *model.HUNTOU2 + 20 * model.HUNTOU3)/100) )

# # lenear
# def objective(model):
#     return (300 + 3 * model.AB1 + 6 * model.AB2 + 9 * model.AB3 + 7 * model.AB4 + 8 * model.AB5 + 9 * model.AB6 + 10 * model.AB7 + 15 * model.FUKUMA_AO1 + 20 * model.FUKUMA_AO2 + 25 * model.FUKUMA_AO3 + 4 * model.CHOUSENSHA1 + 8 * model.CHOUSENSHA2 + 12 * model.CHOUSENSHA3 + 16 * model.CHOUSENSHA4 + 20 * model.CHOUSENSHA5 + 5 * model.SAKAURAMI1 + 10 * model.SAKAURAMI2 + 15 * model.SAKAURAMI3 + 20 * model.SAKAURAMI4 + 25 * model.SAKAURAMI5) * (1.35) * (44/100) * (55/100) * (1.35) 



model.OBJ = pyo.Objective(rule=objective, sense=pyo.maximize)

# opt = SolverFactory("scipampl")
opt = SolverFactory("scip") # solver を scip に変更 (scipamplでは動作しなかった)
result = opt.solve(model, tee=True)
model.display()
print('result: \n', result)

print('variables:')
print('    objective:', model.OBJ())
# print('    x3:', Model.x3())

for v in model.component_data_objects(ctype=pyo.Var):
    print(f"{v.name=}, {v.lb=}, {v.value=}, {v.ub=}")



print('AB:', model.AB0(), model.AB1(), model.AB2(), model.AB3(), model.AB4(), model.AB5(), model.AB6(), model.AB7())

print('FUKUMA:', model.FUKUMA_AKA0(), model.FUKUMA_AKA1(), model.FUKUMA_AKA2(), model.FUKUMA_AKA3(), model.FUKUMA_AO0 (), model.FUKUMA_AO1 (), model.FUKUMA_AO2 (), model.FUKUMA_AO3() )

print('SAKAURAMI:', model.SAKAURAMI0(), model.SAKAURAMI1(), model.SAKAURAMI2(), model.SAKAURAMI3(), model.SAKAURAMI4(), model.SAKAURAMI5())

print('MIKIRI:', model.MIKIRI0(), model.MIKIRI1(), model.MIKIRI2(), model.MIKIRI3(), model.MIKIRI4(), model.MIKIRI5(), model.MIKIRI6(), model.MIKIRI7())

print('CHOUSENSHA:', model.CHOUSENSHA0(), model.CHOUSENSHA1(), model.CHOUSENSHA2(), model.CHOUSENSHA3(), model.CHOUSENSHA4(), model.CHOUSENSHA5())

print('HUNTOU:', model.HUNTOU0(), model.HUNTOU1(), model.HUNTOU2(), model.HUNTOU3())

print('CHOUKAISIN:', model.CHOUKAISIN0(), model.CHOUKAISIN1(), model.CHOUKAISIN2(), model.CHOUKAISIN3())

