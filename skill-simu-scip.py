########################
# p(i, j) := 装備 i の属性 j の値 (係数)
# q(i) := { 0: 装備 i を使わない, 1: 装備 i を使う } (ソルバーで決める変数)
# r(skill, level) := シミュレータに入力される必須スキル (係数)
#   skill = required_skills[]

from pyomo.environ import *
# import pyomo.environ as pyo
from pyomo.opt import SolverFactory

import equipdata as data


print(data.armors[1])

# 存在するスキルの集合
skill_set = set()
remain_slot_set = {'Lv1RemainSlotNum', 'Lv2RemainSlotNum', 'Lv3RemainSlotNum', 'Lv4RemainSlotNum'}
type_set = {'head', 'torso', 'arms', 'waist', 'legs', } # あとで charm を追加する

# 装備の全属性の集合
attribute_set = set()
attribute_set = attribute_set | remain_slot_set | type_set | {'deffence'}

# 装備の名前集合
equip_names = set()

for armor in data.armors:
    # attribute_set.add(armor['type'])
    equip_names.add(armor['name'])
    for skill in armor['skills']:
        attribute_set.add(skill)
        skill_set.add(skill)

for deco in data.decos:
    equip_names.add(deco['name'])
    for skill in deco['skills']:
        attribute_set.add(skill)
        skill_set.add(skill)


print(attribute_set)
print(len(attribute_set))

# 全スキルが存在するかチェック
for skill in attribute_set:
    if not skill in data.allskills:
        print('attribute_set to data.allskills', skill, 'Not Found')

for skill in data.allskills:
    if not skill in attribute_set:
        print('allskills to attr', skill, 'Not Found')


mdl = ConcreteModel(name="Sample", doc="sample model for using scip") # name doc は省略可


# # variable
# mdl.I = RangeSet(0, 7)



# # ダメージ計算用スキル変数
# #   mdl.x['AttackBoost', 3] = 1 ならば AttackBoost Lv.3 が発動
# #   mdl.x['AttackBoost', 1] = 0 ならば AttackBoost Lv.1 が発動しない
# #   sum(mdl.x['AttackBoost', i] for i in [0, ..., 7]) == 1
# mdl.x = Var(skill_set, mdl.I, within=Boolean)



# 防具名で引く辞書用インデックス
# equip_names = ['ルドロス', 'アケノ', 'メルゼ', 'ボロス']

# # データを読み込んできて各防具に存在する属性の set (重複不可) を作成する
# equip_infos = [
#     'head',
#     'torso',
#     'waist',
#     'arms',
#     'legs',
#     'Lv1RemainSlot',
#     'Lv2RemainSlot',
#     'Lv3RemainSlot',
#     'Lv4RemainSlot',
#     'AttackBoost',
#     'DerelictionRed',
#     'DerelictionBlue',
#     'Resentment',
#     'CriticalEye',
#     'Agitator',
#     'Strife',
#     'CriticalBoost',
#    ]


# # 防具データに存在する属性のみ埋める (存在しない属性は mdl.p = Param(..., default= ) で指定される)
# eq_dict = {
#     "ルドロス": {
#         'head': 1,
#         'Lv1RemainSlot': 3,
#         'Lv2RemainSlot': 2,
#         'Lv3RemainSlot': 1,
#         'Lv4RemainSlot': 0,
#         'AttackBoost': 3,
#         'CriticalEye': 2,
#     },
#     "アケノ": {
#         'head': 1,
#         'Lv1RemainSlot': 4,
#         'Lv2RemainSlot': 3,
#         'Lv3RemainSlot': 1,
#         'Lv4RemainSlot': 1,
#         'Strife': 1,
#         'AttackBoost': 2,
#     },

# }

# # パラメータ mdl.p の initialize に渡す用に変形
# eqinfo_matrix = {}
# for eq in eq_dict:
#     for at in eq_dict[eq]:
#         eqinfo_matrix[eq, at] = eq_dict[eq][at]

eqinfo_matrix = {}
for armor in data.armors:
    eqinfo_matrix[armor['name'], armor['type']] = 1
    # skills
    for skill in armor['skills']:
        eqinfo_matrix[armor['name'], skill] = armor['skills'][skill]
    # remain slots
    eqinfo_matrix[armor['name'], 'Lv1RemainSlotNum'] = len(list(filter(lambda n: n >= 1, armor['slots'])))
    eqinfo_matrix[armor['name'], 'Lv2RemainSlotNum'] = len(list(filter(lambda n: n >= 2, armor['slots'])))
    eqinfo_matrix[armor['name'], 'Lv3RemainSlotNum'] = len(list(filter(lambda n: n >= 3, armor['slots'])))
    eqinfo_matrix[armor['name'], 'Lv4RemainSlotNum'] = len(list(filter(lambda n: n >= 4, armor['slots'])))
    eqinfo_matrix[armor['name'], 'deffence'] = armor['deffence']
 
for deco in data.decos:
    # skills
    for skill in deco['skills']:
        eqinfo_matrix[deco['name'], skill] = deco['skills'][skill]
    # remain slots
    eqinfo_matrix[deco['name'], 'Lv1RemainSlotNum'] = -1 if deco['size'] >= 1 else 0
    eqinfo_matrix[deco['name'], 'Lv2RemainSlotNum'] = -1 if deco['size'] >= 2 else 0
    eqinfo_matrix[deco['name'], 'Lv3RemainSlotNum'] = -1 if deco['size'] >= 3 else 0
    eqinfo_matrix[deco['name'], 'Lv4RemainSlotNum'] = -1 if deco['size'] >= 4 else 0


# information of the equipment
mdl.p = Param(equip_names, attribute_set, default=0, initialize=eqinfo_matrix, within=Integers)
# mdl.p = Param([1,2,3], [1,2,3], default=0)

# for eqname in equip_names:
#     for eqinfo in equip_infos:
#         print(eqname, eqinfo, ':', mdl.p[eqname, eqinfo])
# print(mdl.p[1,1])

# number of equipments used
# ある装備を使うか否か
mdl.q = Var(equip_names, within=NonNegativeIntegers) 

# required_skills = {
#     'スタミナ急速回復': 3,
#     '体術': 2,
#     '攻撃': 4,
#     '氷属性攻撃強化': 5,
# }

required_skills = {
    'スタミナ急速回復': 3,
    '体術': 2,
    '攻撃': 4,
    '氷属性攻撃強化': 5,
    '弱点特効': 3,
    '超会心': 3,
    '通常弾・連射矢強化': 3,
    '弾導強化': 1,
    '装填速度': 2,
    '弓溜め段階解放': 1,
}

required_skill_set = {key for key in required_skills}
print(required_skill_set)

mdl.r = Param(skill_set, default=0, initialize=required_skills, within=Integers)

# 各部位で使用できる装備の数は 1 以下
def const_total_equipment_type(mdl, eqtype):
    # print(sum(mdl.q[eqname]*mdl.p[eqname,eqtype] for eqname in equip_names))
    return sum(mdl.q[eqname]*mdl.p[eqname,eqtype] for eqname in equip_names) <= 1

mdl.const_total_equipment_type = Constraint(type_set, rule=const_total_equipment_type)

# Lv別の 空きスロット数 >= 装飾品数
def const_remain_slot_num(mdl, slotlevel):
    # print('\n slotlevel:', slotlevel)
    # print(sum(mdl.q[eqname]*mdl.p[eqname,slotlevel] for eqname in equip_names))
    return sum(mdl.q[eqname]*mdl.p[eqname,slotlevel] for eqname in equip_names) >= 0

mdl.const_remain_slot_num = Constraint(remain_slot_set, rule=const_remain_slot_num)




# 指定された スキル と スキルポイント数 を満たす
def const_skill_point(mdl, skill):
    # print(sum(sum(mdl.q[eqname]*mdl.p[eqname,skill] for eqname in equip_names)))
    return sum(mdl.q[eqname]*mdl.p[eqname,skill] for eqname in equip_names) >= mdl.r[skill]

mdl.const_skill_point = Constraint(required_skill_set, rule=const_skill_point)


# スキルシミュ実装を先に実装するために一時的にコメントアウト
# # スキルシミュ側とダメージ計算に利用するスキルポイント数を結びつける制約式
# #   (全防具のスキルAのポイント数合計) >= (ダメージ計算内のスキルA変数のポイント数合計)
# def const_skill_bridge(mdl):
#     print(sum(mdl.q[eqname]*mdl.p[eqname,'AttackBoost'] for eqname in equip_names))
#     print('>= \n', sum(mdl.I[i+1]*mdl.x['AttackBoost',i] for i in mdl.I))
#     return sum(mdl.q[eqname]*mdl.p[eqname,'AttackBoost'] for eqname in equip_names) \
#                 >= sum(mdl.I[i+1]*mdl.x['AttackBoost',i] for i in mdl.I)

# mdl.const_skill_bridge = Constraint(rule=const_skill_bridge)


# none lenear problem
def objective(mdl):
    return sum(mdl.q[eqname]*mdl.p[eqname,'deffence'] for eqname in equip_names)

mdl.OBJ = Objective(rule=objective, sense=maximize)

opt = SolverFactory("scip") # solver を scip に変更 (scipamplでは動作しなかった)
result = opt.solve(mdl, tee=True)
# mdl.display()
print('result: \n', result)

print('variables:')
print('    objective:', mdl.OBJ())

for v in mdl.component_data_objects(ctype=Var):
    if v.value != 0:
        print(f"{v.name=}, {v.lb=}, {v.value=}, {v.ub=}")


