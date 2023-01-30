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



# 防具名で引く辞書用インデックス
equip_names = ['ルドロス', 'アケノ', 'メルゼ', 'ボロス']

# データを読み込んできて各防具に存在する属性の set (重複不可) を作成する
equip_infos = [
    'head',
    'torso',
    'waist',
    'arms',
    'legs',
    'Lv1RemainSlot',
    'Lv2RemainSlot',
    'Lv3RemainSlot',
    'Lv4RemainSlot',
    'AttackBoost',
    'DerelictionRed',
    'DerelictionBlue',
    'Resentment',
    'CriticalEye',
    'Agitator',
    'Strife',
    'CriticalBoost',
   ]

eqinfo_matrix = {}

eq_dict = {
    "ルドロス": {
        'head': 1,
        'Lv1RemainSlot': 3,
        'Lv2RemainSlot': 2,
        'Lv3RemainSlot': 1,
        'Lv4RemainSlot': 0,
        'AttackBoost': 3,
        'CriticalEye': 2,
    },
    "アケノ": {
        'head': 1,
        'Lv1RemainSlot': 4,
        'Lv2RemainSlot': 3,
        'Lv3RemainSlot': 1,
        'Lv4RemainSlot': 1,
        'Strife': 1,
        'AttackBoost': 2,
    },

}

for eq in eq_dict:
    for at in eq_dict[eq]:
        eqinfo_matrix[eq, at] = eq_dict[eq][at]

# information of the equipment
mdl.p = Param(equip_names, equip_infos, default=0, initialize=eqinfo_matrix)
# mdl.p = Param([1,2,3], [1,2,3], default=0)

for eqname in equip_names:
    for eqinfo in equip_infos:
        print(eqname, eqinfo, ':', mdl.p[eqname, eqinfo])
# print(mdl.p[1,1])

# number of equipments used
mdl.q = Var(equip_names, within=Boolean) 

print(mdl.p['ルドロス','head'])

def const_1(mdl):
    # return mdl.c[1] * mdl.x["AB"] + mdl.c[2] * mdl.x["CB"] + mdl.c[3] * mdl.x["WE"] <= 60
    # return sum(mdl.x[i] for i in key_list)  + sum(mdl.x[i] for i in key_list) <= 60
    # return mdl.q['ルドロス'] * mdl.p['ルドロス']['head'] + mdl.q['アケノ'] * mdl.q['アケノ']['head'] <= 1
    # print(equip_names)
    # print([eqname for eqname in equip_names])
    print(sum(mdl.q[eqname]*mdl.p[eqname,'head'] for eqname in equip_names))
    return sum(mdl.q[eqname]*mdl.p[eqname,'head'] for eqname in equip_names) <= 1

mdl.const_1 = Constraint(rule=const_1)

# スキルシミュ側とダメージ計算に利用するスキルポイント数を結びつける制約式
#   (全防具のスキルAのポイント数合計) >= (ダメージ計算内のスキルA変数のポイント数合計)
def const_skill_bridge(mdl):
    print(sum(mdl.q[eqname]*mdl.p[eqname,'AttackBoost'] for eqname in equip_names))
    print('>= \n', sum(mdl.I[i+1]*mdl.x['AttackBoost',i] for i in mdl.I))


    return sum(mdl.q[eqname]*mdl.p[eqname,'AttackBoost'] for eqname in equip_names) \
                >= sum(mdl.I[i+1]*mdl.x['AttackBoost',i] for i in mdl.I)

mdl.const_skill_bridge = Constraint(rule=const_skill_bridge)

