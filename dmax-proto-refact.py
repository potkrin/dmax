from pyomo.environ import *
# import pyomo.environ as pyo
from pyomo.opt import SolverFactory



mdl = ConcreteModel(name="Sample", doc="sample model for using scip") # name doc は省略可

# variable
mdl.I = RangeSet(0, 7)

skill_list = [
    'AttackBoost',
    'DerelictionRed',
    'DerelictionBlue',
    'Resentment',
    'CriticalEye',
    'Agitator',
    'Strife',
    'CriticalBoost',
]

mdl.x = Var(skill_list, mdl.I, within=Boolean)

# constraints
def const_sameSkill(mdl, skill):
    print('const_sameSkill:', skill)
    return sum(mdl.x[skill, i] for i in mdl.I) == 1

mdl.const_sameSkill = Constraint(skill_list, rule=const_sameSkill)

# def const_AttackBoost(mdl):
#     return sum(mdl.x['AttackBoost', i] for i in range(0,8)) == 1
# mdl.const_AttackBoost = Constraint(rule=const_AttackBoost)

# def const_DerelictionRed(mdl):
#     return sum(mdl.x['DerelictionRed', i] for i in range(0,8)) == 1
# mdl.const_DerelictionRed = Constraint(rule=const_DerelictionRed)

# def const_DerelictionBlue(mdl):
#     return sum(mdl.x['DerelictionBlue', i] for i in range(0,8)) == 1
# mdl.const_DerelictionBlue = Constraint(rule=const_DerelictionBlue)

# def const_Agitator(mdl):
#     return sum(mdl.x['Agitator', i] for i in range(0,8)) == 1
# mdl.const_Agitator = Constraint(rule=const_Agitator)

# def const_Resentment(mdl):
#     return sum(mdl.x['Resentment', i] for i in range(0,8)) == 1
# mdl.const_Resentment = Constraint(rule=const_Resentment)

# def const_CriticalEye(mdl):
#     return sum(mdl.x['CriticalEye', i] for i in range(0,8)) == 1
# mdl.const_CriticalEye = Constraint(rule=const_CriticalEye)

# def const_Strife(mdl):
#     return sum(mdl.x['Strife', i] for i in range(0,8)) == 1
# mdl.const_Strife = Constraint(rule=const_Strife)

# def const_CriticalBoost(mdl):
#     return sum(mdl.x['CriticalBoost', i] for i in range(0,8)) == 1
# mdl.const_CriticalBoost = Constraint(rule=const_CriticalBoost)



def const_total_skill_num(mdl):
    # cannot use slice for mdl.I
    #   make an subset and pass it 
    subset = {t for t in mdl.I if t > 0}
    print('subset:\n',subset)
    print([i for i in subset])
    print(sum(mdl.I[i+1]*mdl.x[skill, i] for skill in skill_list for i in subset))
    return 11 >= (sum(mdl.I[i+1]*mdl.x[skill, i] for skill in skill_list for i in subset)) # use mdl.I[i+1] because RangeSet is 1-index

    # return 11 >= \
    #     mdl.x['AttackBoost',1] + 2*mdl.x['AttackBoost',2] + 3*mdl.x['AttackBoost',3] + 4*mdl.x['AttackBoost',4] + 5*mdl.x['AttackBoost',5] +  6*mdl.x['AttackBoost',6] +  7*mdl.x['AttackBoost',7] + \
    #     mdl.x['DerelictionRed',1] + 2*mdl.x['DerelictionRed',2] + 3*mdl.x['DerelictionRed',3] + \
    #     mdl.x['DerelictionBlue',1] + 2*mdl.x['DerelictionBlue',2] + 3*mdl.x['DerelictionBlue',3] + \
    #     mdl.x['Agitator',1] + 2*mdl.x['Agitator',2] + 3*mdl.x['Agitator',3] + 4*mdl.x['Agitator',4] + 5*mdl.x['Agitator',5] + \
    #     mdl.x['Resentment',1] + 2*mdl.x['Resentment',2] + 3*mdl.x['Resentment',3] + 4*mdl.x['Resentment',4] + 5*mdl.x['Resentment',5] + \
    #     mdl.x['Strife',1] + 2*mdl.x['Strife',2] + 3*mdl.x['Strife',3] + \
    #     mdl.x['CriticalEye',1] + 2*mdl.x['CriticalEye',2] + 3*mdl.x['CriticalEye',3] + 4*mdl.x['CriticalEye',4] + 5*mdl.x['CriticalEye',5] +  6*mdl.x['CriticalEye',6] +  7*mdl.x['CriticalEye',7] + \
    #     mdl.x['CriticalBoost',1] + 2*mdl.x['CriticalBoost',2] + 3*mdl.x['CriticalBoost',3]





mdl.const_total_skill_num = Constraint(rule=const_total_skill_num)


# # ((武器倍率) * (攻撃スキル) + (攻撃スキル加算 + 伏魔響命青 + 逆恨み)) * (物理溜め補正)
# #     * (モーション値 / 100) *(肉質/100) * (強撃ビン補正) *(1.0 - (会心補正 - 1.0)
# #     * (武器会心率 + 見切り + 挑戦者 + 奮闘))

# none lenear problem
def objective(mdl):
    return ( 300*(1.0 + 0.05*mdl.x['AttackBoost',4] + 0.06*mdl.x['AttackBoost',5] + 0.08*mdl.x['AttackBoost',6] + 0.1*mdl.x['AttackBoost',7]) + \
    3*mdl.x['AttackBoost',1]+ 6*mdl.x['AttackBoost',2] + 9*mdl.x['AttackBoost',3] + 7*mdl.x['AttackBoost',4] + 8*mdl.x['AttackBoost',5] + 9*mdl.x['AttackBoost',6] + 10*mdl.x['AttackBoost',7] + \
    15*mdl.x['DerelictionBlue',1] + 20*mdl.x['DerelictionBlue',2] + 25*mdl.x['DerelictionBlue',3] + \
    4*mdl.x['Agitator',1] + 8*mdl.x['Agitator',2] + 12*mdl.x['Agitator',3] + 16*mdl.x['Agitator',4] + 20*mdl.x['Agitator',5] + \
    5*mdl.x['Resentment',1] + 10*mdl.x['Resentment',2] + 15*mdl.x['Resentment',3] + 20*mdl.x['Resentment',4] + 25*mdl.x['Resentment',5] ) * \
    (1.35)*(44/100)*(55/100)*(1.35)* \
    (1 + (1.25 + (0.05*mdl.x['CriticalBoost',1] + 0.1*mdl.x['CriticalBoost',2] + 0.15*mdl.x['CriticalBoost',3]) -1.0) * \
        ((0 + 5*mdl.x['CriticalEye',1] + 10*mdl.x['CriticalEye',2] + 15*mdl.x['CriticalEye',3] + 20*mdl.x['CriticalEye',4] + 25*mdl.x['CriticalEye',5] + 30*mdl.x['CriticalEye',6] + 40*mdl.x['CriticalEye',7] + \
            3*mdl.x['Agitator',1] + 5*mdl.x['Agitator',2] + 7*mdl.x['Agitator',3] + 10*mdl.x['Agitator',4] + 15*mdl.x['Agitator',5] + \
            10*mdl.x['Strife',1] + 15 *mdl.x['Strife',2] + 20*mdl.x['Strife',3])/100) )



# # # lenear
# # def objective(mdl):
# #     return (300 + 3 * mdl.AB1 + 6 * mdl.AB2 + 9 * mdl.AB3 + 7 * mdl.AB4 + 8 * mdl.AB5 + 9 * mdl.AB6 + 10 * mdl.AB7 + 15 * mdl.FUKUMA_AO1 + 20 * mdl.FUKUMA_AO2 + 25 * mdl.FUKUMA_AO3 + 4 * mdl.CHOUSENSHA1 + 8 * mdl.CHOUSENSHA2 + 12 * mdl.CHOUSENSHA3 + 16 * mdl.CHOUSENSHA4 + 20 * mdl.CHOUSENSHA5 + 5 * mdl.SAKAURAMI1 + 10 * mdl.SAKAURAMI2 + 15 * mdl.SAKAURAMI3 + 20 * mdl.SAKAURAMI4 + 25 * mdl.SAKAURAMI5) * (1.35) * (44/100) * (55/100) * (1.35) 


mdl.OBJ = Objective(rule=objective, sense=maximize)

opt = SolverFactory("scip") # solver を scip に変更 (scipamplでは動作しなかった)
result = opt.solve(mdl, tee=True)
mdl.display()
print('result: \n', result)

print('variables:')
print('    objective:', mdl.OBJ())

for v in mdl.component_data_objects(ctype=Var):
    print(f"{v.name=}, {v.lb=}, {v.value=}, {v.ub=}")


