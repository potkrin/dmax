# skill-simu-scip.py に 簡易的なダメージ計算式 を追加する (dmaxのプロトタイプ)


########################
# p(i, j) := 装備 i の属性 j の値 (係数)
# q(i) := { 0: 装備 i を使わない, 1: 装備 i を使う } (ソルバーで決める変数)
# r(skill, level) := シミュレータに入力される必須スキル (係数)
#   skill = required_skills[]

from pyomo.environ import *
from pyomo.opt import SolverFactory

import equipdata as data
import sys

# ダメージ式用の定数
cp = {
    "武器倍率": 380.0,
    "溜め補正物理": 1.35,
    "モーション値": 11.0,
    "肉質": 55.0,
    "ビン補正": 1.35,
    "武器会心率": 0.0,
}


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


# variable

# スキルレベルのインデックス (すべて最大レベル7に統一))
mdl.I = RangeSet(0, 7)

# ダメージ計算式に登場するスキル名の集合
damage_skill_set = {
    "攻撃",
    "伏魔響命",
    "逆恨み",
    "見切り",
    "挑戦者",
    "奮闘",
    "超会心",
}

# affinity_skill_set = {
#     "見切り",
#     "挑戦者",
#     "奮闘",
# }

# ダメージ計算用スキル変数
#   mdl.x['AttackBoost', 3] = 1 ならば AttackBoost Lv.3 が発動
#   mdl.x['AttackBoost', 1] = 0 ならば AttackBoost Lv.1 が発動しない
#   sum(mdl.x['AttackBoost', i] for i in [0, ..., 7]) == 1
mdl.x = Var(damage_skill_set, mdl.I, within=Boolean)

# 会心率の合計 mdl.af <= 100 AND mdl.af <= 5*mdl.x[会心スキル1,1] + 10*mdl.x[会心スキル1,2]
mdl.af = Var(within=NonNegativeIntegers)


# 装備(防具･装飾品･護石) のデータを用意する
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

# number of equipments used
# ある装備を使うか否か
mdl.q = Var(equip_names, within=NonNegativeIntegers, initialize=0) 

# 必須スキルを指定 (ユーザーが入力)
#   例: 奮闘連射弓 -> 奮闘3, 弾導強化1, 装填速度2, 弓溜め段階解放1
required_skills = {
    # 'スタミナ急速回復': 3, '体術': 2, '攻撃': 4, '氷属性攻撃強化': 5, '弱点特効': 3, '超会心': 3, '通常弾・連射矢強化': 3, '弾導強化': 1, '装填速度': 2, '弓溜め段階解放': 1,

    # '弱点特効': 3,
    # '超会心': 3,
    '通常弾・連射矢強化': 3,
    '弾導強化': 1,
    '装填速度': 2,
    '弓溜め段階解放': 1,
    # '伏魔響命': 1,
    # '奮闘': 3,
    # '攻撃': 2,
    # '見切り': 7,
    # '氷属性攻撃強化': 5,

    # '風纏': 3,

    # '弓溜め段階解放':1, '奮闘':3, '狂化':1, '伏魔響命':2, '見切り':6, '逆恨み':3, '超会心':2, '弱点特効【属性】':1, '狂竜症【蝕】':1, '災禍転福':3, '弱点特効':3, '通常弾・連射矢強化':3, '氷属性攻撃強化':3
    
    # '弱点特効':3, '攻撃':7, '見切り':3, '超会心':3, '納刀術':3, '翔蟲使い':3, '鋼殻の恩恵':3, '風纏':1, '粉塵纏':1, '連撃':1, 'フルチャージ':1, '渾身':2, '風圧耐性':3

    # '弱点特効':3, '超会心':3, '翔蟲使い':3, '顕如盤石':3, '砲弾装填':2, '攻撃':4, '研磨術【鋭】':1, '弱点特効【属性】':1, 'チャージマスター':2, '会心撃【属性】':2, '逆恨み':2, '弾丸節約':2, '笛吹き名人':1

}



# スキル名が有効かチェック (入力データの検証)
for skill in required_skills:
    print('skill input check:', skill)
    if not skill in skill_set:
        print(skill, 'NOT FOUND Exit')
        sys.exit(1)
    

required_skill_set = {key for key in required_skills}
print(required_skill_set)

mdl.r = Param(skill_set, default=0, initialize=required_skills, within=Integers)

# 各部位で使用できる装備の数は 1 以下
def const_total_equipment_type(mdl, eqtype):
    # print(sum(mdl.q[eqname]*mdl.p[eqname,eqtype] for eqname in equip_names), '\n <= 1')
    return sum(mdl.q[eqname]*mdl.p[eqname,eqtype] for eqname in equip_names) <= 1

mdl.const_total_equipment_type = Constraint(type_set, rule=const_total_equipment_type)

# Lv別の 空きスロット数 >= 装飾品数
def const_remain_slot_num(mdl, slotlevel):
    # print('\n slotlevel:', slotlevel)
    # print(sum(mdl.q[eqname]*mdl.p[eqname,slotlevel] for eqname in equip_names), '\n>= 0')
    return sum(mdl.q[eqname]*mdl.p[eqname,slotlevel] for eqname in equip_names) >= 0

mdl.const_remain_slot_num = Constraint(remain_slot_set, rule=const_remain_slot_num)




# 指定された スキル と スキルポイント数 を満たす
def const_skill_point(mdl, skill):
    print(sum(mdl.q[eqname]*mdl.p[eqname,skill] for eqname in equip_names), '\n >= \n', mdl.r[skill])
    return sum(mdl.q[eqname]*mdl.p[eqname,skill] for eqname in equip_names) >= mdl.r[skill]

mdl.const_skill_point = Constraint(required_skill_set, rule=const_skill_point)



# ダメージ計算部分の追加
def const_skill_level_total(mdl, skill):
    # <= 1 でもいいかもしれない
    return sum(mdl.x[skill, i] for i in mdl.I) == 1 

mdl.const_skill_level_total = Constraint(damage_skill_set, rule=const_skill_level_total)

# スキルシミュ側とダメージ計算に利用するスキルポイント数を結びつける制約式
#   (全防具のスキルAのポイント数合計) >= (ダメージ計算内のスキルA変数のポイント数合計)
def const_skill_bridge(mdl, skill):
    return sum(mdl.q[eqname]*mdl.p[eqname, skill] for eqname in equip_names) \
            >= sum(mdl.I[i+1]*mdl.x[skill, i] for i in mdl.I)

mdl.const_skill_bridge = Constraint(damage_skill_set, rule=const_skill_bridge)

def const_max_affinity(mdl):
    return mdl.af <= 100

mdl.const_max_affinity = Constraint(rule=const_max_affinity)


def const_max_affinity_2(mdl):
    return mdl.af <= (cp['武器会心率'] + 5*mdl.x['見切り',1] + 10*mdl.x['見切り',2] + 15*mdl.x['見切り',3] + 20*mdl.x['見切り',4] + 25*mdl.x['見切り',5] + 30*mdl.x['見切り',6] + 40*mdl.x['見切り',7]\
           + 10*mdl.x['奮闘',1] + 15*mdl.x['奮闘',2] + 20*mdl.x['奮闘',3]\
           + 3*mdl.x['挑戦者',1] + 5*mdl.x['挑戦者',2] + 7*mdl.x['挑戦者',3] + 10*mdl.x['挑戦者',4] + 15*mdl.x['挑戦者',5])

mdl.const_max_affinity_2 = Constraint(rule=const_max_affinity_2)



# ダメージ計算式メモ
# MUL1 = cp['武器倍率'] * (1.0 + 0.05*bp['攻撃'][4] + 0.06*bp['攻撃'][5] + 0.08*bp['攻撃'][6] + 0.1*bp['攻撃'][7])

# ADD = MUL1 + 3*bp['攻撃'][1] + 6*bp['攻撃'][2] + 9*bp['攻撃'][3] + 7*bp['攻撃'][4] + 8*bp['攻撃'][5] + 9*bp['攻撃'][6] + 10*bp['攻撃'][7]\
#       + 25*bp['伏魔響命・青'][1] + 30*bp['伏魔響命・青'][2] + 35*bp['伏魔響命・青'][3]\
#       + 5*bp['逆恨み'][1] + 10*bp['逆恨み'][2] + 15*bp['逆恨み'][3] + 20*bp['逆恨み'][4] + 25*bp['逆恨み'][5]\
#       + 4*bp['挑戦者'][1] + 8*bp['挑戦者'][2] + 12*bp['挑戦者'][3] + 16*bp['挑戦者'][4] + 20*bp['挑戦者'][5]\

# AFFR = (min(100.0, cp['武器会心率'] + 5*bp['見切り'][1] + 10*bp['見切り'][2] + 15*bp['見切り'][3] + 20*bp['見切り'][4] + 25*bp['見切り'][5] + 30*bp['見切り'][6] + 40*bp['見切り'][7]\
#                       + 10*bp['奮闘'][1] + 15*bp['奮闘'][2] + 20*bp['奮闘'][3]\
#                       + 3*bp['挑戦者'][1] + 5*bp['挑戦者'][2] + 7*bp['挑戦者'][3] + 10*bp['挑戦者'][4] + 15*bp['挑戦者'][5]))/100.0

# MUL2 = ADD * cp['溜め補正物理'] * (cp['モーション値']/100.0) *  (cp['肉質']/100.0) * cp['ビン補正']\
#        * (1.0 + (AFFR) * (1.25 + 0.05*bp['超会心'][1] + 0.1*bp['超会心'][2] + 0.15*bp['超会心'][3] - 1.0))

# この制約では 100 を大きく超えるパターンが網羅出来ない
# # constraint 会心率 100以下
# def const_max_affinity(mdl)
#     # できれば レベルごと会心率などのデータも ベクトル変数で管理 (複数効果のものはどうするか?)
#     return mdl.x[]
#     return 100 >= (cp['武器会心率'] + 5*mdl.x['見切り',1] + 10*mdl.x['見切り',2] + 15*mdl.x['見切り',3] + 20*mdl.x['見切り',4] + 25*mdl.x['見切り',5] + 30*mdl.x['見切り',6] + 40*mdl.x['見切り',7]\
#                       + 10*mdl.x['奮闘',1] + 15*mdl.x['奮闘',2] + 20*mdl.x['奮闘',3]\
#                       + 3*mdl.x['挑戦者',1] + 5*mdl.x['挑戦者',2] + 7*mdl.x['挑戦者',3] + 10*mdl.x['挑戦者',4] + 15*mdl.x['挑戦者',5])


# none lenear problem
def objective(mdl):
    # return sum(mdl.q[eqname]*mdl.p[eqname,'deffence'] for eqname in equip_names)
    return (cp['武器倍率'] * (1.0 + 0.05*mdl.x['攻撃',4] + 0.06*mdl.x['攻撃',5] + 0.08*mdl.x['攻撃',6] + 0.1*mdl.x['攻撃',7])\
           + 3*mdl.x['攻撃',1] + 6*mdl.x['攻撃',2] + 9*mdl.x['攻撃',3] + 7*mdl.x['攻撃',4] + 8*mdl.x['攻撃',5] + 9*mdl.x['攻撃',6] + 10*mdl.x['攻撃',7]\
           + 25*mdl.x['伏魔響命',1] + 30*mdl.x['伏魔響命',2] + 35*mdl.x['伏魔響命',3]\
           + 5*mdl.x['逆恨み',1] + 10*mdl.x['逆恨み',2] + 15*mdl.x['逆恨み',3] + 20*mdl.x['逆恨み',4] + 25*mdl.x['逆恨み',5]\
           + 4*mdl.x['挑戦者',1] + 8*mdl.x['挑戦者',2] + 12*mdl.x['挑戦者',3] + 16*mdl.x['挑戦者',4] + 20*mdl.x['挑戦者',5])\
           * cp['溜め補正物理'] * (cp['モーション値']/100.0) *  (cp['肉質']/100.0) * cp['ビン補正']\
           * (1.0 + (((mdl.af))/100.0\
                    ) * (1.25 + 0.05*mdl.x['超会心',1] + 0.1*mdl.x['超会心',2] + 0.15*mdl.x['超会心',3] - 1.0))





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


