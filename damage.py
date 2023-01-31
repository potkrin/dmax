# ダメージ計算式が間違っているので注意
# - 伏魔青の倍率が違う 
# - 会心の期待値計算が違う

import pyomo.environ as pyo
from pyomo.opt import SolverFactory

model = pyo.ConcreteModel(name="Sample", doc="sample model for using scip") # name doc は省略可

model.AB0  = 1
model.AB1  = 0
model.AB2  = 0
model.AB3  = 0
model.AB4  = 0
model.AB5  = 0
model.AB6  = 0
model.AB7  = 0

model.FUKUMA_AKA0  = 1
model.FUKUMA_AKA1  = 0
model.FUKUMA_AKA2  = 0
model.FUKUMA_AKA3  = 0
model.FUKUMA_AO0  = 0
model.FUKUMA_AO1  = 0
model.FUKUMA_AO2  = 0
model.FUKUMA_AO3  = 0

model.SAKAURAMI0  = 1
model.SAKAURAMI1  = 0
model.SAKAURAMI2  = 0
model.SAKAURAMI3  = 0
model.SAKAURAMI4  = 0
model.SAKAURAMI5  = 0

model.MIKIRI0  = 1
model.MIKIRI1  = 0
model.MIKIRI2  = 0
model.MIKIRI3  = 0
model.MIKIRI4  = 0
model.MIKIRI5  = 0
model.MIKIRI6  = 0
model.MIKIRI7  = 0

model.CHOUSENSHA0  = 1
model.CHOUSENSHA1  = 0
model.CHOUSENSHA2  = 0
model.CHOUSENSHA3  = 0
model.CHOUSENSHA4  = 0
model.CHOUSENSHA5  = 0

model.HUNTOU0  = 1
model.HUNTOU1  = 0
model.HUNTOU2  = 0
model.HUNTOU3  = 0
model.HUNTOU4  = 0
model.HUNTOU5  = 0

model.CHOUKAISIN0  = 1
model.CHOUKAISIN1  = 0
model.CHOUKAISIN2  = 0
model.CHOUKAISIN3  = 0


mul1 = (300 * (1.0 *(model.AB0 + model.AB1 + model.AB2 + model.AB3) + 1.05 * model.AB4 + 1.06 * model.AB5 + 1.08 * model.AB6 + 1.1 * model.AB7))

plus = (300 * (1.0 *(model.AB0 + model.AB1 + model.AB2 + model.AB3) + 1.05 * model.AB4 + 1.06 * model.AB5 + 1.08 * model.AB6 + 1.1 * model.AB7) + 3 * model.AB1 + 6 * model.AB2 + 9 * model.AB3 + 7 * model.AB4 + 8 * model.AB5 + 9 * model.AB6 + 10 * model.AB7 + 15 * model.FUKUMA_AO1 + 20 * model.FUKUMA_AO2 + 25 * model.FUKUMA_AO3 + 4 * model.CHOUSENSHA1 + 8 * model.CHOUSENSHA2 + 12 * model.CHOUSENSHA3 + 16 * model.CHOUSENSHA4 + 20 * model.CHOUSENSHA5 + 5 * model.SAKAURAMI1 + 10 * model.SAKAURAMI2 + 15 * model.SAKAURAMI3 + 20 * model.SAKAURAMI4 + 25 * model.SAKAURAMI5)

mul2 = (300 * (1.0 *(model.AB0 + model.AB1 + model.AB2 + model.AB3) + 1.05 * model.AB4 + 1.06 * model.AB5 + 1.08 * model.AB6 + 1.1 * model.AB7) + 3 * model.AB1 + 6 * model.AB2 + 9 * model.AB3 + 7 * model.AB4 + 8 * model.AB5 + 9 * model.AB6 + 10 * model.AB7 + 15 * model.FUKUMA_AO1 + 20 * model.FUKUMA_AO2 + 25 * model.FUKUMA_AO3 + 4 * model.CHOUSENSHA1 + 8 * model.CHOUSENSHA2 + 12 * model.CHOUSENSHA3 + 16 * model.CHOUSENSHA4 + 20 * model.CHOUSENSHA5 + 5 * model.SAKAURAMI1 + 10 * model.SAKAURAMI2 + 15 * model.SAKAURAMI3 + 20 * model.SAKAURAMI4 + 25 * model.SAKAURAMI5) * (1.35) * (11/100) * (55/100) * (1.35)

kaisin = (0 + 5 * model.MIKIRI1 + 10 * model.MIKIRI2 + 15 * model.MIKIRI3 + 20 * model.MIKIRI4 + 25 * model.MIKIRI5 + 30 * model.MIKIRI6 + 40 * model.MIKIRI7 + 3 * model.CHOUSENSHA1 + 5 * model.CHOUSENSHA2 + 7 * model.CHOUSENSHA3 + 10 * model.CHOUSENSHA4 + 15 * model.CHOUSENSHA5 + 10 * model.HUNTOU1 + 15 *model.HUNTOU2 + 20 * model.HUNTOU3)/100

kaisinhosei = (1 + (1.25 * model.CHOUKAISIN0 + 1.30 * model.CHOUKAISIN1 + 1.35 * model.CHOUKAISIN2 + 1.4 * model.CHOUKAISIN3 -1.0) * ((0 + 5 * model.MIKIRI1 + 10 * model.MIKIRI2 + 15 * model.MIKIRI3 + 20 * model.MIKIRI4 + 25 * model.MIKIRI5 + 30 * model.MIKIRI6 + 40 * model.MIKIRI7 + 3 * model.CHOUSENSHA1 + 5 * model.CHOUSENSHA2 + 7 * model.CHOUSENSHA3 + 10 * model.CHOUSENSHA4 + 15 * model.CHOUSENSHA5 + 10 * model.HUNTOU1 + 15 *model.HUNTOU2 + 20 * model.HUNTOU3)/100) )

damage = (300 * (1.0 *(model.AB0 + model.AB1 + model.AB2 + model.AB3) + 1.05 * model.AB4 + 1.06 * model.AB5 + 1.08 * model.AB6 + 1.1 * model.AB7) + 3 * model.AB1 + 6 * model.AB2 + 9 * model.AB3 + 7 * model.AB4 + 8 * model.AB5 + 9 * model.AB6 + 10 * model.AB7 + 15 * model.FUKUMA_AO1 + 20 * model.FUKUMA_AO2 + 25 * model.FUKUMA_AO3 + 4 * model.CHOUSENSHA1 + 8 * model.CHOUSENSHA2 + 12 * model.CHOUSENSHA3 + 16 * model.CHOUSENSHA4 + 20 * model.CHOUSENSHA5 + 5 * model.SAKAURAMI1 + 10 * model.SAKAURAMI2 + 15 * model.SAKAURAMI3 + 20 * model.SAKAURAMI4 + 25 * model.SAKAURAMI5) * (1.35) * (11/100) * (55/100) * (1.35) * (1 + (1.25 * model.CHOUKAISIN0 + 1.30 * model.CHOUKAISIN1 + 1.35 * model.CHOUKAISIN2 + 1.4 * model.CHOUKAISIN3 -1.0) * ((0 + 5 * model.MIKIRI1 + 10 * model.MIKIRI2 + 15 * model.MIKIRI3 + 20 * model.MIKIRI4 + 25 * model.MIKIRI5 + 30 * model.MIKIRI6 + 40 * model.MIKIRI7 + 3 * model.CHOUSENSHA1 + 5 * model.CHOUSENSHA2 + 7 * model.CHOUSENSHA3 + 10 * model.CHOUSENSHA4 + 15 * model.CHOUSENSHA5 + 10 * model.HUNTOU1 + 15 *model.HUNTOU2 + 20 * model.HUNTOU3)/100) )

print('mul1 = ', mul1)
print('plus = ', plus)
print('mul2 = ', mul2)
print('kaisin = ', kaisin)
print('kaisinhosei = ', kaisinhosei)
print('damage = ', damage)
