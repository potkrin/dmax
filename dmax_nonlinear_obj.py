# dmax のプロトタイプ
# 簡易的なダメージ計算式を スキルシミュによる制約の元 最大化することができる
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

import urllib.parse # スキルシミュに投げる用のURLの作成に利用

import csv 
import copy

# 元データ に 傀異錬成防具 や 護石 データを追加したもの
armor_all = copy.deepcopy(data.armors)


with open('data_charms.csv') as f:
    charms = csv.reader(f)
    for charm in charms:
        print()
        for i in range(7):
            print(charm[i], type(charm[i]))

        temp_charm = {
            "rare":0,
            "type":"charm",
            "name": "護石【" + charm[0] + "，" + charm[2] + "】", # なんでもいい (けど skillA skillB 3-1-1 形式のほうがいいかも?))
            "deffence":0,
            "fire":"0",
            "water":"0",
            "ice":"0",
            "thunder":"0",
            "dragon":"0",
            "slots":[],
            "skills":{}
        }
        for i in range(4,7):
            if charm[i] != '0':
                temp_charm["slots"].append(int(charm[i]))

        for i in range(2):
            if charm[2*i] != '':
                temp_charm["skills"][charm[2*i]] = int(charm[2*i+1])

        print("temp_charm:", temp_charm)
        armor_all.append(temp_charm)

with open('data_augments.csv') as f:
    augments = csv.reader(f)
    for augment in augments:
        print()
        print(augment)
        
        for base_armor in data.armors:
            if augment[0] == base_armor['name']:
                print("Base armor found: name = ", base_armor['name'])
                temp_augment = {
                    "rare":0,
                    "type":base_armor['type'],
                    # リバルカイザーホーン,0,0,0,0,0,0,1,0,0,巧撃,1,skill,lv,skill,lv,skill,lv,,
                    # 0: name,
                    # 1: deffence,
                    # 2: fire,
                    # 3: water,
                    # 4: thunder,
                    # 5: ice,
                    # 6: dragon,
                    # 7: slot1,
                    # 8: slot2,
                    # 9: slot3,
                    # 10:skill1name,
                    # 11: lv,
                    # 12:skill2name,
                    # 13: lv,
                    # 14:skill3name,
                    # 15: lv,
                    # 16:skill4name,
                    # 17: lv,
                    # 18,
                    # 19
                    "name": "", # 下でつくる
                    "deffence": base_armor['deffence'] + int(augment[1]),
                    "fire": base_armor['fire'] + augment[2],          # fire などの値が string になっている
                    "water": base_armor['water'] + augment[3],
                    "ice": base_armor['ice'] + augment[4],
                    "thunder": base_armor['thunder'] + augment[5],
                    "draon": base_armor['dragon'] + augment[6],
                    "slots":[],
                    "skills":{}
                }

                # 名前作成 防具名(スキルA+N, ))
                aug_name = augment[0] + '('
                for i in range(4):
                    skill_name = augment[10+2*i]
                    if skill_name == '':
                        continue

                    diff_level = int(augment[10+2*i+1])

                    if diff_level >= 0:
                        aug_name += skill_name + '+' + str(diff_level)
                    else:
                        aug_name += skill_name + str(diff_level)

               
                slot_count = 0
                for i in range(3):
                    if augment[7+i] != '0':
                        slot_count += int(augment[7+i])
                aug_name += 'スロット' + str(slot_count) + ')'

                temp_augment['name'] = aug_name

                # スロット情報設定
                for i in range(3):
                    if len(base_armor['slots']) > i:
                        base_level = base_armor['slots'][i]
                    else:
                        base_level = 0

                    skill_level = base_level + int(augment[7+i])
                    print('base_level=', base_level, 'skill_level=', skill_level)

                    if skill_level > 0:
                        temp_augment['slots'].append(skill_level)
                
                # スキル情報設定
                for skill in base_armor['skills']:
                    temp_augment['skills'][skill] = base_armor['skills'][skill]

                for i in range(4):
                    adding_skill = augment[10+2*i]
                    if adding_skill != '':
                        if adding_skill in base_armor['skills']:
                            temp_augment['skills'][adding_skill] = base_armor['skills'][adding_skill] + int(augment[10+2*i+1])
                        else:
                            temp_augment['skills'][adding_skill] = int(augment[10+2*i+1])

                print('base_augment = ', base_armor)
                print('temp_augment = ', temp_augment)
                armor_all.append(temp_augment)
                break

#             if base_armor['name'] == data.armors[len(data.armors)-1]['name']:
#                 print("Base Armor not Found: name = ", augment[0])
#                 print(augment[0] == '')


        # temp_augment = {
        #     "rare":0,
        #     "type":"augment",
        #     "name": "護石【" + augment[0] + "，" + augment[2] + "】", # なんでもいい (けど skillA skillB 3-1-1 形式のほうがいいかも?))
        #     "deffence":0,
        #     "fire":"0",
        #     "water":"0",
        #     "ice":"0",
        #     "thunder":"0",
        #     "dragon":"0",
        #     "slots":[],
        #     "skills":{augment[0]:int(augment[1]), augment[2]:int(augment[3]), }
        # }
        # for i in range(4,7):
        #     if augment[i] != '0':
        #         temp_augment["slots"].append(int(augment[i]))

        # print("temp_augment:", temp_augment)
        # data.armors.append(temp_augment)




# ダメージ式用の定数
cp = {
    "武器倍率": 360.0,
    "武器属性値": 22.0,
    "属性": [False, False, False, True, False, False, ], # 無属性, 火, 水, 氷, 雷, 龍
    "武器会心率": 0.0,
    "溜め補正物理": 1.35, #溜め4
    "溜め補正属性": 1.2, #溜め4
    "モーション値": 11.0, #連射Lv5
    "ビン補正": 1.35, #強撃ビン

    "物理肉質": 70.0,
    "属性肉質": 15.0,

    "百竜装飾品" : {"弱点特効【属性】": 0, "種系特効": 1, "やられ特効": 0, "劫血活性": [0, 0, 0], "鋼龍の魂": 0, "天彗龍の魂": 0},
    "矢強化": 1,
    "剛力の弓がけ": 0,
    "ヒトダマドリ": 0.0,
    "アミキリアカネ": 0.0, # 0 or 1
    "強化咆哮": 0, # 0 or 1
    "鬼人薬": [0, 0, 0], # 0: なし, 1: 鬼人薬, 2: 鬼人薬G
    "力の護符": 1,
    "力の爪": 1,
    "種ホムラ": [0, 1, 0], # 0: なし, 1: 怪力の種, 2: ホムラチョウ
    "鬼人の粉塵": 1,
    "お団子火事場力": [0, 0, 1],
    "強化太鼓の技": 0,
    "にらみ撃ち": 0,
    "射撃術": [0, 0, 0, 0, 1],
    "短期催眠": [0, 1, 0, 0, 0],
    "怒り補正": 1.0, 

    "SSW": [True, False],
    "闇討ち": [False, False, False, False], # 闇討ちLv0, 1, 2, 3
    "弾強化": [False, False, False, True],
    "矢タイプ": "通常弾・連射矢強化",
    # "矢タイプ": "散弾・拡散矢強化",
    # "矢タイプ": "貫通弾・貫通矢強化",

    # 矢強化
    # 剛力
    # にらみ撃ち
    # 百竜装飾品
    # 火事場
    # 強化太鼓
    # バフアイテム
    # 射撃術
}




# 存在するスキルの集合
skill_set = set()
remain_slot_set = {'Lv1RemainSlotNum', 'Lv2RemainSlotNum', 'Lv3RemainSlotNum', 'Lv4RemainSlotNum'}
type_set = {'head', 'torso', 'arms', 'waist', 'legs', 'charm'} # あとで charm を追加する

# 装備の全属性の集合
attribute_set = set()
attribute_set = attribute_set | remain_slot_set | type_set | {'deffence'}

# 装備の名前集合
equip_names = set()

for armor in armor_all:
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


mdl = ConcreteModel(name="dmax model", doc="model for solving damage optimization problem") # name doc は省略可


# variable

# スキルレベルのインデックス (すべて最大レベル7に統一))
mdl.I = RangeSet(0, 7)

# ダメージ計算式に登場するスキル名の集合
damage_skill_set = {
    "攻撃",
    "見切り",
    "伏魔響命",
    "業鎧【修羅】",
    "火属性攻撃強化",
    "水属性攻撃強化",
    "氷属性攻撃強化",
    "雷属性攻撃強化",
    "龍属性攻撃強化",
    "挑戦者",
    "逆恨み",
    "龍気活性", # 0-51気活性, 61気活性
    "奮闘",
    "狂竜症【蝕】", # 正確には 克服 + (狂竜症なし) の 15% も必要
    "災禍転福",
    "連撃",
    "攻勢",
    "巧撃",
    "闇討ち",
    "フルチャージ",
    "逆襲",
    "死中に活",
    "弱点特効",
    "超会心",
    "弱点特効【属性】",
    "会心撃【属性】",
    "チャージマスター",
    "通常弾・連射矢強化",
    "散弾・拡散矢強化",
    "貫通弾・貫通矢強化",
    "渾身",
    "鋼殻の恩恵",
    "炎鱗の恩恵",
}


# 装備(防具･装飾品･護石) のデータを用意する
eqinfo_matrix = {}
for armor in armor_all:
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

    # 'スタミナ急速回復': 3, '体術': 5, '力の解放': 1,

    '弾導強化': 1,
    '装填速度': 2,
    '弓溜め段階解放': 1,
    '奮闘': 3,
    '刃鱗磨き': 1,
    '狂化': 1,
    '回避距離ＵＰ': 1,
    'ＫＯ術': 1,

    # '弱点特効': 3,
    # '超会心': 3,
    # '伏魔響命': 3,
    # '奮闘': 3,
    # '攻撃': 2,
    # '見切り': 7,
    # '氷属性攻撃強化': 5,

    # '風纏': 3,

    # '弓溜め段階解放':1, '奮闘':3, '狂化':1, '伏魔響命':2, '見切り':6, '逆恨み':3, '超会心':2, '弱点特効【属性】':1, '狂竜症【蝕】':1, '災禍転福':3, '弱点特効':3, '通常弾・連射矢強化':3, '氷属性攻撃強化':3
    
    # '弱点特効':3, '攻撃':7, '見切り':3, '超会心':3, '納刀術':3, '翔蟲使い':3, '鋼殻の恩恵':3, '風纏':1, '粉塵纏':1, '連撃':1, 'フルチャージ':1, '渾身':2, '風圧耐性':3

    # '弱点特効':3, '超会心':3, '翔蟲使い':3, '顕如盤石':3, '砲弾装填':2, '攻撃':4, '研磨術【鋭】':1, '弱点特効【属性】':1, 'チャージマスター':2, '会心撃【属性】':2, '逆恨み':2, '弾丸節約':2, '笛吹き名人':1

}


# 矢タイプ定数から 弾強化スキルを追加
if cp['弾強化'][3]:
    required_skills[cp['矢タイプ']] = 3
elif cp['弾強化'][2]:
    required_skills[cp['矢タイプ']] = 2
elif cp['弾強化'][1]:
    required_skills[cp['矢タイプ']] = 1
else:
    required_skills[cp['矢タイプ']] = 0

print('required_skills = \n', required_skills)


# active rate ダメージ要素の発動割合
ar = {
    "攻勢": 0,
    "フルチャージ": 0,
    "逆襲": 0,
    "死中に活": 0,
    "龍気活性": 0,
    "渾身": 1,
    "攻撃": 1,
    "見切り": 1,
    "伏魔響命": 1,
    "業鎧【修羅】": 1,
    "火属性攻撃強化": 1,
    "水属性攻撃強化": 1,
    "氷属性攻撃強化": 1,
    "雷属性攻撃強化": 1,
    "龍属性攻撃強化": 1,
    "挑戦者": 0.7,
    "逆恨み": 1,
    "奮闘": 1,
    # 狂竜症サンプル
    # - https://www.youtube.com/watch?v=O_BuFYMqsL8&t=66s
    # - 0:26 - 0:42 - 1:42 - 2:01 - 3:01 - 3:20
    # - {16, 18, 19}秒 : 60秒
    # - (感染から克服にかかる時間:15~20秒) : (克服中時間:60, 60, 90秒)
    "狂竜症【蝕】": 0.25, # (感染から克服にかかる時間:15~20秒) : (克服中時間:60, 60, 90秒) の割合
    "災禍転福": 0.38, # 狂竜症で発動する場合は 30秒 : (感染-克服-感染 の1サイクル)
    "連撃": 1,
    "巧撃": 1,
    "闇討ち": 1,
    "弱点特効": 1,
    "超会心": 1,
    "弱点特効【属性】": 1,
    "会心撃【属性】": 1,
    "チャージマスター": 1,
    "通常弾・連射矢強化": 1,
    "散弾・拡散矢強化": 1,
    "貫通弾・貫通矢強化": 1,
    "鋼殻の恩恵": 1,
    "炎鱗の恩恵": 1,
}

print('active rate = ', ar)


# スキル名が有効かチェック (入力データの検証)
for skill in required_skills:
    print('skill input check:', skill)
    if not skill in skill_set:
        print(skill, 'NOT FOUND Exit')
        sys.exit(1)
    

required_skill_set = {key for key in required_skills}
print(required_skill_set)

mdl.r = Param(skill_set, default=0, initialize=required_skills, within=Integers)

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

# min(100, 会心率) を実現するために必要
# 会心率の合計 mdl.afr <= 100 AND mdl.afr <= (武器会心+スキル会心の合計)
mdl.afr = Var(within=NonNegativeIntegers)

# 重たいので一旦除外
# # 疾替えの書 mdl.sw[0]: 朱 mdl.sw[1]: 蒼
# mdl.sI = RangeSet(0,1) 
# mdl.ssw = Var(mdl.sI, within=Boolean)

# # 各部位で使用できる装備の数は 1 以下
# def const_switch_skill_swap(mdl):
#     return 1 == (mdl.ssw[0] + mdl.ssw[1])

# mdl.const_switch_skill_swap = Constraint(rule=const_switch_skill_swap)



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
    return mdl.afr <= 100

mdl.const_max_affinity = Constraint(rule=const_max_affinity)


def const_max_affinity_2(mdl):
    # return mdl.afr <= (cp['武器会心率'] + 5*mdl.x['見切り',1] + 10*mdl.x['見切り',2] + 15*mdl.x['見切り',3] + 20*mdl.x['見切り',4] + 25*mdl.x['見切り',5] + 30*mdl.x['見切り',6] + 40*mdl.x['見切り',7]\
    #        + 10*mdl.x['奮闘',1] + 15*mdl.x['奮闘',2] + 20*mdl.x['奮闘',3]\
    #        + 3*mdl.x['挑戦者',1] + 5*mdl.x['挑戦者',2] + 7*mdl.x['挑戦者',3] + 10*mdl.x['挑戦者',4] + 15*mdl.x['挑戦者',5])
           
    # 狂竜症の処理
    return mdl.afr <= \
                (cp['武器会心率'] \
                + 15*cp['百竜装飾品']['鋼龍の魂'] \
                + 50*cp['アミキリアカネ'] \
                + 30*cp['強化咆哮'] \
                + 5*mdl.x['見切り',1] + 10*mdl.x['見切り',2] + 15*mdl.x['見切り',3] \
                + 20*mdl.x['見切り',4] + 25*mdl.x['見切り',5] + 30*mdl.x['見切り',6] + 40*mdl.x['見切り',7] \
                + ar['挑戦者']*(3*mdl.x['挑戦者',1] + 5*mdl.x['挑戦者',2] + 7*mdl.x['挑戦者',3] + 10*mdl.x['挑戦者',4] + 15*mdl.x['挑戦者',5]) \
                + 10*mdl.x['奮闘',1] + 15*mdl.x['奮闘',2] + 20*mdl.x['奮闘',3] \
                + (1.0 - ar['狂竜症【蝕】']) * (20*mdl.x['狂竜症【蝕】',1] + 25*mdl.x['狂竜症【蝕】',2] + 25*mdl.x['狂竜症【蝕】',3]) \
                + ar['攻勢']*(10*mdl.x['攻勢',2] + 20*mdl.x['攻勢',3]) \
                + 15*mdl.x['弱点特効',1] + 30*mdl.x['弱点特効',2] + 50*mdl.x['弱点特効',3] \
                + ar['渾身']*(10*mdl.x['渾身',1] + 20*mdl.x['渾身',2] + 30*mdl.x['渾身',3]))

mdl.const_max_affinity_2 = Constraint(rule=const_max_affinity_2)

# ダメージ計算のパーツ
# mdl.P_MUL1 = Var(within=Reals)
# mdl.P_ADD  = Var(within=Reals)
# mdl.P_MUL2 = Var(within=Reals)

# mdl.E_MUL1 = Var(within=Reals)
# mdl.E_ADD  = Var(within=Reals)
# mdl.E_MUL2 = Var(within=Reals)

# def const_p_mul1(mdl):
#     return mdl.P_MUL1 == (1.0 + 0.05*mdl.x['攻撃',4] + 0.06*mdl.x['攻撃',5] + 0.08*mdl.x['攻撃',6] + 0.1*mdl.x['攻撃',7])

# mdl.const_p_mul1 = Constraint(rule=const_p_mul1)

# def const_p_add(mdl):
#     return mdl.P_ADD == \
#            (3*mdl.x['攻撃',1] + 6*mdl.x['攻撃',2] + 9*mdl.x['攻撃',3] + 7*mdl.x['攻撃',4] + 8*mdl.x['攻撃',5] + 9*mdl.x['攻撃',6] + 10*mdl.x['攻撃',7]\
#            + 25*mdl.x['伏魔響命',1] + 30*mdl.x['伏魔響命',2] + 35*mdl.x['伏魔響命',3]\
#            + 5*mdl.x['逆恨み',1] + 10*mdl.x['逆恨み',2] + 15*mdl.x['逆恨み',3] + 20*mdl.x['逆恨み',4] + 25*mdl.x['逆恨み',5]\
#            + 4*mdl.x['挑戦者',1] + 8*mdl.x['挑戦者',2] + 12*mdl.x['挑戦者',3] + 16*mdl.x['挑戦者',4] + 20*mdl.x['挑戦者',5])

# mdl.const_p_add = Constraint(rule=const_p_add)

# def const_p_mul2(mdl):
#     return mdl.P_MUL2 == \
#            ( cp['溜め補正物理'] * (cp['モーション値']/100.0) *  (cp['肉質']/100.0) * cp['ビン補正'] \
#            * (1.0 + (((mdl.afr))/100.0) * (1.25 + 0.05*mdl.x['超会心',1] + 0.1*mdl.x['超会心',2] + 0.15*mdl.x['超会心',3] - 1.0)))

# mdl.const_p_mul2 = Constraint(rule=const_p_mul2)


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


# この制約では 100 を大きく超えるパターンが網羅出来ない (なので mdl.afr を利用する方法にしました)
# # constraint 会心率 100以下
# def const_max_affinity(mdl)
#     # できれば レベルごと会心率などのデータも ベクトル変数で管理 (複数効果のものはどうするか?)
#     return mdl.x[]
#     return 100 >= (cp['武器会心率'] + 5*mdl.x['見切り',1] + 10*mdl.x['見切り',2] + 15*mdl.x['見切り',3] + 20*mdl.x['見切り',4] + 25*mdl.x['見切り',5] + 30*mdl.x['見切り',6] + 40*mdl.x['見切り',7]\
#                       + 10*mdl.x['奮闘',1] + 15*mdl.x['奮闘',2] + 20*mdl.x['奮闘',3]\
#                       + 3*mdl.x['挑戦者',1] + 5*mdl.x['挑戦者',2] + 7*mdl.x['挑戦者',3] + 10*mdl.x['挑戦者',4] + 15*mdl.x['挑戦者',5])

# SCIP は非線形な目的関数に対応していないので新たに変数を追加して制約条件に移す
mdl.varobj = Var(within=NonNegativeReals)

def const_nonlinear_objective(mdl):
    return mdl.varobj <= \
                (cp['武器倍率'] \
                * (1.0 + 0.3*cp['お団子火事場力'][1] +0.35*cp['お団子火事場力'][2]) \
                * (1.0 + 0.05*cp['強化太鼓の技']) \
                * (1.0 + 0.1*cp['剛力の弓がけ']) \
                * (1.0 + 0.05*mdl.x['龍気活性',4] + 0.1*mdl.x['龍気活性',5]) \
                * (1.0 + 0.05*mdl.x['攻撃',4] + 0.06*mdl.x['攻撃',5] + 0.08*mdl.x['攻撃',6] + 0.1*mdl.x['攻撃',7]) \
                + 5*cp['鬼人薬'][1] + 7*cp['鬼人薬'][2] \
                + 6*cp['力の護符'] \
                + 9*cp['力の爪'] \
                + 10*cp['種ホムラ'][1] + 25*cp['種ホムラ'][2] \
                + 10*cp['鬼人の粉塵'] \
                + 6*cp['短期催眠'][1] + 9*cp['短期催眠'][2] + 12*cp['短期催眠'][3] + 15*cp['短期催眠'][4] \
                + 15*cp['百竜装飾品']['劫血活性'][1] + 30*cp['百竜装飾品']['劫血活性'][2] \
                + cp['ヒトダマドリ'] \
                + 3*mdl.x['攻撃',1] + 6*mdl.x['攻撃',2] + 9*mdl.x['攻撃',3] + 7*mdl.x['攻撃',4] + 8*mdl.x['攻撃',5] + 9*mdl.x['攻撃',6] + 10*mdl.x['攻撃',7] \
                + cp['SSW'][1] * (25*mdl.x['伏魔響命',1] + 30*mdl.x['伏魔響命',2] + 35*mdl.x['伏魔響命',3]) \
                + cp['SSW'][0] * (15*mdl.x['業鎧【修羅】',1] + 25*mdl.x['業鎧【修羅】',2] + 35*mdl.x['業鎧【修羅】',3]) \
                + 4*mdl.x['挑戦者',1] + 8*mdl.x['挑戦者',2] + 12*mdl.x['挑戦者',3] + 16*mdl.x['挑戦者',4] + 20*mdl.x['挑戦者',5] \
                + 5*mdl.x['逆恨み',1] + 10*mdl.x['逆恨み',2] + 15*mdl.x['逆恨み',3] + 20*mdl.x['逆恨み',4] + 25*mdl.x['逆恨み',5] \
                + ar['狂竜症【蝕】']*(10*mdl.x['狂竜症【蝕】',1] + 15*mdl.x['狂竜症【蝕】',2] + 20*mdl.x['狂竜症【蝕】',3])\
                + ar['災禍転福']*(12*mdl.x['災禍転福',1] + 15*mdl.x['災禍転福',2] + 18*mdl.x['災禍転福',3]) \
                + 8*mdl.x['連撃',1] + 9*mdl.x['連撃',2] + 10*mdl.x['連撃',3] \
                + ar['攻勢']*(10*mdl.x['攻勢',1] + 10*mdl.x['攻勢',2] + 15*mdl.x['攻勢',3]) \
                + 10*mdl.x['巧撃',1] + 15*mdl.x['巧撃',2] + 30*mdl.x['巧撃',3] \
                + ar['フルチャージ']*(5*mdl.x['フルチャージ',1] + 10*mdl.x['フルチャージ',2] + 20*mdl.x['フルチャージ',3]) \
                + ar['逆襲']*(10*mdl.x['逆襲',1] + 15*mdl.x['逆襲',2] + 20*mdl.x['逆襲',3]) \
                + ar['死中に活']*(5*mdl.x['死中に活',1] + 10*mdl.x['死中に活',2] + 20*mdl.x['死中に活',3])) \
                * cp['溜め補正物理'] \
                * (cp['モーション値']/100.0) \
                * (1.0 + 0.05*cp['百竜装飾品']['種系特効']) \
                * (1.0 + 0.1*cp['百竜装飾品']['やられ特効']) \
                * (1.0 + 0.05*cp['闇討ち'][1] + 0.1*cp['闇討ち'][2] + 0.2*cp['闇討ち'][3]) \
                * (1.0 + 0.05*cp['弾強化'][1] + 0.1*cp['弾強化'][2] + 0.2*cp['弾強化'][3]) \
                * (cp['物理肉質']/100.0) * cp['ビン補正'] \
                * (1.0 + 0.3*cp['にらみ撃ち']) \
                * (1.0 + 0.15*cp['矢強化']) \
                * (1.0 + 0.01*cp['射撃術'][1] + 0.02*cp['射撃術'][2] + 0.03*cp['射撃術'][3] + 0.04*cp['射撃術'][4]) \
                * (1.0 + (mdl.afr/100.0) * (1.25 + 0.05*mdl.x['超会心',1] + 0.1*mdl.x['超会心',2] + 0.15*mdl.x['超会心',3] - 1.0)) \
            + (1 - cp['属性'][0]) * ((cp['武器属性値'] \
                * (1.0 + 0.1*cp['百竜装飾品']['劫血活性'][1] + 0.2*cp['百竜装飾品']['劫血活性'][2]) \
                * (1.0 + 0.2*cp['百竜装飾品']['天彗龍の魂']) \
                * (1.0 + cp['SSW'][1] * (0.05*mdl.x['業鎧【修羅】',1] +  0.1*mdl.x['業鎧【修羅】',2] +  0.2*mdl.x['業鎧【修羅】',3])) \
                * (1.0 + cp['属性'][1] * (0.05*mdl.x['火属性攻撃強化',3] +  0.1*mdl.x['火属性攻撃強化',4] +  0.2*mdl.x['火属性攻撃強化',5])) \
                * (1.0 + cp['属性'][2] * (0.05*mdl.x['水属性攻撃強化',3] +  0.1*mdl.x['水属性攻撃強化',4] +  0.2*mdl.x['水属性攻撃強化',5])) \
                * (1.0 + cp['属性'][3] * (0.05*mdl.x['氷属性攻撃強化',3] +  0.1*mdl.x['氷属性攻撃強化',4] +  0.2*mdl.x['氷属性攻撃強化',5])) \
                * (1.0 + cp['属性'][4] * (0.05*mdl.x['雷属性攻撃強化',3] +  0.1*mdl.x['雷属性攻撃強化',4] +  0.2*mdl.x['雷属性攻撃強化',5])) \
                * (1.0 + cp['属性'][5] * (0.05*mdl.x['龍属性攻撃強化',3] +  0.1*mdl.x['龍属性攻撃強化',4] +  0.2*mdl.x['龍属性攻撃強化',5])) \
                * (1.0 + 0.1*mdl.x['奮闘',1] +  0.15*mdl.x['奮闘',2] +  0.2*mdl.x['奮闘',3]) \
                * (1.0 + cp['属性'][2] * (0.05*mdl.x['鋼殻の恩恵',1] +  0.1*mdl.x['鋼殻の恩恵',2])) \
                * (1.0 + cp['属性'][3] * (0.05*mdl.x['鋼殻の恩恵',1] +  0.1*mdl.x['鋼殻の恩恵',2])) \
                * (1.0 + cp['属性'][1] * (0.05*mdl.x['炎鱗の恩恵',1] +  0.1*mdl.x['炎鱗の恩恵',2]))) \
                + cp['SSW'][0] * (12*mdl.x['伏魔響命',1] + 15*mdl.x['伏魔響命',2] + 20*mdl.x['伏魔響命',3]) \
                + cp['属性'][1] * (2*mdl.x['火属性攻撃強化',1] +  3*mdl.x['火属性攻撃強化',2] +  4*mdl.x['火属性攻撃強化',3] + 4*mdl.x['火属性攻撃強化',4] +  4*mdl.x['火属性攻撃強化',5]) \
                + cp['属性'][2] * (2*mdl.x['水属性攻撃強化',1] +  3*mdl.x['水属性攻撃強化',2] +  4*mdl.x['水属性攻撃強化',3] + 4*mdl.x['水属性攻撃強化',4] +  4*mdl.x['水属性攻撃強化',5]) \
                + cp['属性'][3] * (2*mdl.x['氷属性攻撃強化',1] +  3*mdl.x['氷属性攻撃強化',2] +  4*mdl.x['氷属性攻撃強化',3] + 4*mdl.x['氷属性攻撃強化',4] +  4*mdl.x['氷属性攻撃強化',5]) \
                + cp['属性'][4] * (2*mdl.x['雷属性攻撃強化',1] +  3*mdl.x['雷属性攻撃強化',2] +  4*mdl.x['雷属性攻撃強化',3] + 4*mdl.x['雷属性攻撃強化',4] +  4*mdl.x['雷属性攻撃強化',5]) \
                + cp['属性'][5] * (2*mdl.x['龍属性攻撃強化',1] +  3*mdl.x['龍属性攻撃強化',2] +  4*mdl.x['龍属性攻撃強化',3] + 4*mdl.x['龍属性攻撃強化',4] +  4*mdl.x['龍属性攻撃強化',5]) \
                + ar['狂竜症【蝕】'] * (5*mdl.x['狂竜症【蝕】',1] + 7*mdl.x['狂竜症【蝕】',2] + 10*mdl.x['狂竜症【蝕】',3]) \
                + ar['災禍転福']*(2*mdl.x['災禍転福',1] + 3*mdl.x['災禍転福',2] + 4*mdl.x['災禍転福',3]) \
                + 6*mdl.x['連撃',1] + 8*mdl.x['連撃',2] + 10*mdl.x['連撃',3]) \
                * (cp['溜め補正属性'] * cp['属性肉質'] / 100.0 \
                * (1.0 + 0.1*cp['百竜装飾品']['劫血活性'][1] + 0.2*cp['百竜装飾品']['劫血活性'][2]) \
                * (1.0 + 0.1*mdl.x['弱点特効【属性】',1] + 0.125*mdl.x['弱点特効【属性】',2] + 0.15*mdl.x['弱点特効【属性】',3]) \
                * (1.0 + 0.05*mdl.x['チャージマスター',1] + 0.1*mdl.x['チャージマスター',2] + 0.15*mdl.x['チャージマスター',3]) \
                * (1.0 + 0.3*cp['にらみ撃ち']) \
                * (1.0 + 0.10*cp['矢強化']) \
                * (1.0 + 0.15*cp['百竜装飾品']['弱点特効【属性】']) \
                * cp['怒り補正'] \
                * (1.0 + (mdl.afr/100.0) * (1.0 + 0.05*mdl.x['会心撃【属性】',1] + 0.1*mdl.x['会心撃【属性】',2] + 0.15*mdl.x['会心撃【属性】',3] - 1.0)))

def const_nonlinear_objective_physics(mdl):
    return mdl.varobj <= (cp['武器倍率'] \
                * (1.0 + 0.3*cp['お団子火事場力'][1] +0.35*cp['お団子火事場力'][2]) \
                * (1.0 + 0.05*cp['強化太鼓の技']) \
                * (1.0 + 0.1*cp['剛力の弓がけ']) \
                * (1.0 + 0.05*mdl.x['龍気活性',4] + 0.1*mdl.x['龍気活性',5]) \
                * (1.0 + 0.05*mdl.x['攻撃',4] + 0.06*mdl.x['攻撃',5] + 0.08*mdl.x['攻撃',6] + 0.1*mdl.x['攻撃',7]) \
                + 5*cp['鬼人薬'][1] + 7*cp['鬼人薬'][2] \
                + 6*cp['力の護符'] \
                + 9*cp['力の爪'] \
                + 10*cp['種ホムラ'][1] + 25*cp['種ホムラ'][2] \
                + 10*cp['鬼人の粉塵'] \
                + 6*cp['短期催眠'][1] + 9*cp['短期催眠'][2] + 12*cp['短期催眠'][3] + 15*cp['短期催眠'][4] \
                + 15*cp['百竜装飾品']['劫血活性'][1] + 30*cp['百竜装飾品']['劫血活性'][2] \
                + cp['ヒトダマドリ'] \
                + 3*mdl.x['攻撃',1] + 6*mdl.x['攻撃',2] + 9*mdl.x['攻撃',3] + 7*mdl.x['攻撃',4] + 8*mdl.x['攻撃',5] + 9*mdl.x['攻撃',6] + 10*mdl.x['攻撃',7] \
                + cp['SSW'][1] * (25*mdl.x['伏魔響命',1] + 30*mdl.x['伏魔響命',2] + 35*mdl.x['伏魔響命',3]) \
                + cp['SSW'][0] * (15*mdl.x['業鎧【修羅】',1] + 25*mdl.x['業鎧【修羅】',2] + 35*mdl.x['業鎧【修羅】',3]) \
                + 4*mdl.x['挑戦者',1] + 8*mdl.x['挑戦者',2] + 12*mdl.x['挑戦者',3] + 16*mdl.x['挑戦者',4] + 20*mdl.x['挑戦者',5] \
                + 5*mdl.x['逆恨み',1] + 10*mdl.x['逆恨み',2] + 15*mdl.x['逆恨み',3] + 20*mdl.x['逆恨み',4] + 25*mdl.x['逆恨み',5] \
                + ar['狂竜症【蝕】']*(10*mdl.x['狂竜症【蝕】',1] + 15*mdl.x['狂竜症【蝕】',2] + 20*mdl.x['狂竜症【蝕】',3])\
                + ar['災禍転福']*(12*mdl.x['災禍転福',1] + 15*mdl.x['災禍転福',2] + 18*mdl.x['災禍転福',3]) \
                + 8*mdl.x['連撃',1] + 9*mdl.x['連撃',2] + 10*mdl.x['連撃',3] \
                + ar['攻勢']*(10*mdl.x['攻勢',1] + 10*mdl.x['攻勢',2] + 15*mdl.x['攻勢',3]) \
                + 10*mdl.x['巧撃',1] + 15*mdl.x['巧撃',2] + 30*mdl.x['巧撃',3] \
                + ar['フルチャージ']*(5*mdl.x['フルチャージ',1] + 10*mdl.x['フルチャージ',2] + 20*mdl.x['フルチャージ',3]) \
                + ar['逆襲']*(10*mdl.x['逆襲',1] + 15*mdl.x['逆襲',2] + 20*mdl.x['逆襲',3]) \
                + ar['死中に活']*(5*mdl.x['死中に活',1] + 10*mdl.x['死中に活',2] + 20*mdl.x['死中に活',3])) \
                * cp['溜め補正物理'] \
                * (cp['モーション値']/100.0) \
                * (1.0 + 0.05*cp['百竜装飾品']['種系特効']) \
                * (1.0 + 0.1*cp['百竜装飾品']['やられ特効']) \
                * (1.0 + 0.05*cp['闇討ち'][1] + 0.1*cp['闇討ち'][2] + 0.2*cp['闇討ち'][3]) \
                * (1.0 + 0.05*cp['弾強化'][1] + 0.1*cp['弾強化'][2] + 0.2*cp['弾強化'][3]) \
                * (cp['物理肉質']/100.0) * cp['ビン補正'] \
                * (1.0 + 0.3*cp['にらみ撃ち']) \
                * (1.0 + 0.15*cp['矢強化']) \
                * (1.0 + 0.01*cp['射撃術'][1] + 0.02*cp['射撃術'][2] + 0.03*cp['射撃術'][3] + 0.04*cp['射撃術'][4]) \
                * (1.0 + (mdl.afr/100.0) * (1.25 + 0.05*mdl.x['超会心',1] + 0.1*mdl.x['超会心',2] + 0.15*mdl.x['超会心',3] - 1.0))
 

# mdl.const_nonlinear_objective = Constraint(rule=const_nonlinear_objective)
# mdl.const_nonlinear_objective_physics = Constraint(rule=const_nonlinear_objective_physics)





def objective(mdl):
    return mdl.varobj


# none lenear problem
def objective_nonlinear(mdl):
    # return (cp['武器倍率'] * (1.0 + 0.05*mdl.x['攻撃',4] + 0.06*mdl.x['攻撃',5] + 0.08*mdl.x['攻撃',6] + 0.1*mdl.x['攻撃',7]) \
    #        + 3*mdl.x['攻撃',1] + 6*mdl.x['攻撃',2] + 9*mdl.x['攻撃',3] + 7*mdl.x['攻撃',4] + 8*mdl.x['攻撃',5] + 9*mdl.x['攻撃',6] + 10*mdl.x['攻撃',7] \
    #        + mdl.ssw[1] * (25*mdl.x['伏魔響命',1] + 30*mdl.x['伏魔響命',2] + 35*mdl.x['伏魔響命',3]) \
    #        + 5*mdl.x['逆恨み',1] + 10*mdl.x['逆恨み',2] + 15*mdl.x['逆恨み',3] + 20*mdl.x['逆恨み',4] + 25*mdl.x['逆恨み',5] \
    #        + 4*mdl.x['挑戦者',1] + 8*mdl.x['挑戦者',2] + 12*mdl.x['挑戦者',3] + 16*mdl.x['挑戦者',4] + 20*mdl.x['挑戦者',5]) \
    #        * cp['溜め補正物理'] * (cp['モーション値']/100.0) *  (cp['肉質']/100.0) * cp['ビン補正'] \
    #        * (1.0 + (((mdl.afr))/100.0 \
    #                 ) * (1.25 + 0.05*mdl.x['超会心',1] + 0.1*mdl.x['超会心',2] + 0.15*mdl.x['超会心',3] - 1.0))
    # #return (mdl.P_MUL1 + mdl.P_ADD) * mdl.P_MUL2

    return (cp['武器倍率'] \
                * (1.0 + 0.3*cp['お団子火事場力'][1] +0.35*cp['お団子火事場力'][2]) \
                * (1.0 + 0.05*cp['強化太鼓の技']) \
                * (1.0 + 0.1*cp['剛力の弓がけ']) \
                * (1.0 + 0.05*mdl.x['龍気活性',4] + 0.1*mdl.x['龍気活性',5]) \
                * (1.0 + 0.05*mdl.x['攻撃',4] + 0.06*mdl.x['攻撃',5] + 0.08*mdl.x['攻撃',6] + 0.1*mdl.x['攻撃',7]) \
                + 5*cp['鬼人薬'][1] + 7*cp['鬼人薬'][2] \
                + 6*cp['力の護符'] \
                + 9*cp['力の爪'] \
                + 10*cp['種ホムラ'][1] + 25*cp['種ホムラ'][2] \
                + 10*cp['鬼人の粉塵'] \
                + 6*cp['短期催眠'][1] + 9*cp['短期催眠'][2] + 12*cp['短期催眠'][3] + 15*cp['短期催眠'][4] \
                + 15*cp['百竜装飾品']['劫血活性'][1] + 30*cp['百竜装飾品']['劫血活性'][2] \
                + cp['ヒトダマドリ'] \
                + 3*mdl.x['攻撃',1] + 6*mdl.x['攻撃',2] + 9*mdl.x['攻撃',3] + 7*mdl.x['攻撃',4] + 8*mdl.x['攻撃',5] + 9*mdl.x['攻撃',6] + 10*mdl.x['攻撃',7] \
                + cp['SSW'][1] * (25*mdl.x['伏魔響命',1] + 30*mdl.x['伏魔響命',2] + 35*mdl.x['伏魔響命',3]) \
                + cp['SSW'][0] * (15*mdl.x['業鎧【修羅】',1] + 25*mdl.x['業鎧【修羅】',2] + 35*mdl.x['業鎧【修羅】',3]) \
                + 4*mdl.x['挑戦者',1] + 8*mdl.x['挑戦者',2] + 12*mdl.x['挑戦者',3] + 16*mdl.x['挑戦者',4] + 20*mdl.x['挑戦者',5] \
                + 5*mdl.x['逆恨み',1] + 10*mdl.x['逆恨み',2] + 15*mdl.x['逆恨み',3] + 20*mdl.x['逆恨み',4] + 25*mdl.x['逆恨み',5] \
                + ar['狂竜症【蝕】']*(10*mdl.x['狂竜症【蝕】',1] + 15*mdl.x['狂竜症【蝕】',2] + 20*mdl.x['狂竜症【蝕】',3])\
                + ar['災禍転福']*(12*mdl.x['災禍転福',1] + 15*mdl.x['災禍転福',2] + 18*mdl.x['災禍転福',3]) \
                + 8*mdl.x['連撃',1] + 9*mdl.x['連撃',2] + 10*mdl.x['連撃',3] \
                + ar['攻勢']*(10*mdl.x['攻勢',1] + 10*mdl.x['攻勢',2] + 15*mdl.x['攻勢',3]) \
                + 10*mdl.x['巧撃',1] + 15*mdl.x['巧撃',2] + 30*mdl.x['巧撃',3] \
                + ar['フルチャージ']*(5*mdl.x['フルチャージ',1] + 10*mdl.x['フルチャージ',2] + 20*mdl.x['フルチャージ',3]) \
                + ar['逆襲']*(10*mdl.x['逆襲',1] + 15*mdl.x['逆襲',2] + 20*mdl.x['逆襲',3]) \
                + ar['死中に活']*(5*mdl.x['死中に活',1] + 10*mdl.x['死中に活',2] + 20*mdl.x['死中に活',3])) \
                * cp['溜め補正物理'] \
                * (cp['モーション値']/100.0) \
                * (1.0 + 0.05*cp['百竜装飾品']['種系特効']) \
                * (1.0 + 0.1*cp['百竜装飾品']['やられ特効']) \
                * (1.0 + 0.05*cp['闇討ち'][1] + 0.1*cp['闇討ち'][2] + 0.2*cp['闇討ち'][3]) \
                * (1.0 + 0.05*cp['弾強化'][1] + 0.1*cp['弾強化'][2] + 0.2*cp['弾強化'][3]) \
                * (cp['物理肉質']/100.0) * cp['ビン補正'] \
                * (1.0 + 0.3*cp['にらみ撃ち']) \
                * (1.0 + 0.15*cp['矢強化']) \
                * (1.0 + 0.01*cp['射撃術'][1] + 0.02*cp['射撃術'][2] + 0.03*cp['射撃術'][3] + 0.04*cp['射撃術'][4]) \
                * (1.0 + (mdl.afr/100.0) * (1.25 + 0.05*mdl.x['超会心',1] + 0.1*mdl.x['超会心',2] + 0.15*mdl.x['超会心',3] - 1.0)) \
            + (1 - cp['属性'][0]) * ((cp['武器属性値'] \
                * (1.0 + 0.1*cp['百竜装飾品']['劫血活性'][1] + 0.2*cp['百竜装飾品']['劫血活性'][2]) \
                * (1.0 + 0.2*cp['百竜装飾品']['天彗龍の魂']) \
                * (1.0 + cp['SSW'][1] * (0.05*mdl.x['業鎧【修羅】',1] +  0.1*mdl.x['業鎧【修羅】',2] +  0.2*mdl.x['業鎧【修羅】',3])) \
                * (1.0 + cp['属性'][1] * (0.05*mdl.x['火属性攻撃強化',3] +  0.1*mdl.x['火属性攻撃強化',4] +  0.2*mdl.x['火属性攻撃強化',5])) \
                * (1.0 + cp['属性'][2] * (0.05*mdl.x['水属性攻撃強化',3] +  0.1*mdl.x['水属性攻撃強化',4] +  0.2*mdl.x['水属性攻撃強化',5])) \
                * (1.0 + cp['属性'][3] * (0.05*mdl.x['氷属性攻撃強化',3] +  0.1*mdl.x['氷属性攻撃強化',4] +  0.2*mdl.x['氷属性攻撃強化',5])) \
                * (1.0 + cp['属性'][4] * (0.05*mdl.x['雷属性攻撃強化',3] +  0.1*mdl.x['雷属性攻撃強化',4] +  0.2*mdl.x['雷属性攻撃強化',5])) \
                * (1.0 + cp['属性'][5] * (0.05*mdl.x['龍属性攻撃強化',3] +  0.1*mdl.x['龍属性攻撃強化',4] +  0.2*mdl.x['龍属性攻撃強化',5])) \
                * (1.0 + 0.1*mdl.x['奮闘',1] +  0.15*mdl.x['奮闘',2] +  0.2*mdl.x['奮闘',3]) \
                * (1.0 + cp['属性'][2] * (0.05*mdl.x['鋼殻の恩恵',1] +  0.1*mdl.x['鋼殻の恩恵',2])) \
                * (1.0 + cp['属性'][3] * (0.05*mdl.x['鋼殻の恩恵',1] +  0.1*mdl.x['鋼殻の恩恵',2])) \
                * (1.0 + cp['属性'][1] * (0.05*mdl.x['炎鱗の恩恵',1] +  0.1*mdl.x['炎鱗の恩恵',2]))) \
                + cp['SSW'][0] * (12*mdl.x['伏魔響命',1] + 15*mdl.x['伏魔響命',2] + 20*mdl.x['伏魔響命',3]) \
                + cp['属性'][1] * (2*mdl.x['火属性攻撃強化',1] +  3*mdl.x['火属性攻撃強化',2] +  4*mdl.x['火属性攻撃強化',3] + 4*mdl.x['火属性攻撃強化',4] +  4*mdl.x['火属性攻撃強化',5]) \
                + cp['属性'][2] * (2*mdl.x['水属性攻撃強化',1] +  3*mdl.x['水属性攻撃強化',2] +  4*mdl.x['水属性攻撃強化',3] + 4*mdl.x['水属性攻撃強化',4] +  4*mdl.x['水属性攻撃強化',5]) \
                + cp['属性'][3] * (2*mdl.x['氷属性攻撃強化',1] +  3*mdl.x['氷属性攻撃強化',2] +  4*mdl.x['氷属性攻撃強化',3] + 4*mdl.x['氷属性攻撃強化',4] +  4*mdl.x['氷属性攻撃強化',5]) \
                + cp['属性'][4] * (2*mdl.x['雷属性攻撃強化',1] +  3*mdl.x['雷属性攻撃強化',2] +  4*mdl.x['雷属性攻撃強化',3] + 4*mdl.x['雷属性攻撃強化',4] +  4*mdl.x['雷属性攻撃強化',5]) \
                + cp['属性'][5] * (2*mdl.x['龍属性攻撃強化',1] +  3*mdl.x['龍属性攻撃強化',2] +  4*mdl.x['龍属性攻撃強化',3] + 4*mdl.x['龍属性攻撃強化',4] +  4*mdl.x['龍属性攻撃強化',5]) \
                + ar['狂竜症【蝕】'] * (5*mdl.x['狂竜症【蝕】',1] + 7*mdl.x['狂竜症【蝕】',2] + 10*mdl.x['狂竜症【蝕】',3]) \
                + ar['災禍転福']*(2*mdl.x['災禍転福',1] + 3*mdl.x['災禍転福',2] + 4*mdl.x['災禍転福',3]) \
                + 6*mdl.x['連撃',1] + 8*mdl.x['連撃',2] + 10*mdl.x['連撃',3]) \
                * (cp['溜め補正属性'] * cp['属性肉質'] / 100.0 \
                * (1.0 + 0.1*cp['百竜装飾品']['劫血活性'][1] + 0.2*cp['百竜装飾品']['劫血活性'][2]) \
                * (1.0 + 0.1*mdl.x['弱点特効【属性】',1] + 0.125*mdl.x['弱点特効【属性】',2] + 0.15*mdl.x['弱点特効【属性】',3]) \
                * (1.0 + 0.05*mdl.x['チャージマスター',1] + 0.1*mdl.x['チャージマスター',2] + 0.15*mdl.x['チャージマスター',3]) \
                * (1.0 + 0.3*cp['にらみ撃ち']) \
                * (1.0 + 0.10*cp['矢強化']) \
                * (1.0 + 0.15*cp['百竜装飾品']['弱点特効【属性】']) \
                * cp['怒り補正'] \
                * (1.0 + (mdl.afr/100.0) * (1.0 + 0.05*mdl.x['会心撃【属性】',1] + 0.1*mdl.x['会心撃【属性】',2] + 0.15*mdl.x['会心撃【属性】',3] - 1.0)))

# none lenear problem
def objective_physics_only(mdl):
    return (cp['武器倍率'] \
                * (1.0 + 0.3*cp['お団子火事場力'][1] +0.35*cp['お団子火事場力'][2]) \
                * (1.0 + 0.05*cp['強化太鼓の技']) \
                * (1.0 + 0.1*cp['剛力の弓がけ']) \
                * (1.0 + 0.05*mdl.x['龍気活性',4] + 0.1*mdl.x['龍気活性',5]) \
                * (1.0 + 0.05*mdl.x['攻撃',4] + 0.06*mdl.x['攻撃',5] + 0.08*mdl.x['攻撃',6] + 0.1*mdl.x['攻撃',7]) \
                + 5*cp['鬼人薬'][1] + 7*cp['鬼人薬'][2] \
                + 6*cp['力の護符'] \
                + 9*cp['力の爪'] \
                + 10*cp['種ホムラ'][1] + 25*cp['種ホムラ'][2] \
                + 10*cp['鬼人の粉塵'] \
                + 6*cp['短期催眠'][1] + 9*cp['短期催眠'][2] + 12*cp['短期催眠'][3] + 15*cp['短期催眠'][4] \
                + 15*cp['百竜装飾品']['劫血活性'][1] + 30*cp['百竜装飾品']['劫血活性'][2] \
                + cp['ヒトダマドリ'] \
                + 3*mdl.x['攻撃',1] + 6*mdl.x['攻撃',2] + 9*mdl.x['攻撃',3] + 7*mdl.x['攻撃',4] + 8*mdl.x['攻撃',5] + 9*mdl.x['攻撃',6] + 10*mdl.x['攻撃',7] \
                + cp['SSW'][1] * (25*mdl.x['伏魔響命',1] + 30*mdl.x['伏魔響命',2] + 35*mdl.x['伏魔響命',3]) \
                + cp['SSW'][0] * (15*mdl.x['業鎧【修羅】',1] + 25*mdl.x['業鎧【修羅】',2] + 35*mdl.x['業鎧【修羅】',3]) \
                + 4*mdl.x['挑戦者',1] + 8*mdl.x['挑戦者',2] + 12*mdl.x['挑戦者',3] + 16*mdl.x['挑戦者',4] + 20*mdl.x['挑戦者',5] \
                + 5*mdl.x['逆恨み',1] + 10*mdl.x['逆恨み',2] + 15*mdl.x['逆恨み',3] + 20*mdl.x['逆恨み',4] + 25*mdl.x['逆恨み',5] \
                + ar['狂竜症【蝕】']*(10*mdl.x['狂竜症【蝕】',1] + 15*mdl.x['狂竜症【蝕】',2] + 20*mdl.x['狂竜症【蝕】',3])\
                + ar['災禍転福']*(12*mdl.x['災禍転福',1] + 15*mdl.x['災禍転福',2] + 18*mdl.x['災禍転福',3]) \
                + 8*mdl.x['連撃',1] + 9*mdl.x['連撃',2] + 10*mdl.x['連撃',3] \
                + ar['攻勢']*(10*mdl.x['攻勢',1] + 10*mdl.x['攻勢',2] + 15*mdl.x['攻勢',3]) \
                + 10*mdl.x['巧撃',1] + 15*mdl.x['巧撃',2] + 30*mdl.x['巧撃',3] \
                + ar['フルチャージ']*(5*mdl.x['フルチャージ',1] + 10*mdl.x['フルチャージ',2] + 20*mdl.x['フルチャージ',3]) \
                + ar['逆襲']*(10*mdl.x['逆襲',1] + 15*mdl.x['逆襲',2] + 20*mdl.x['逆襲',3]) \
                + ar['死中に活']*(5*mdl.x['死中に活',1] + 10*mdl.x['死中に活',2] + 20*mdl.x['死中に活',3])) \
                * cp['溜め補正物理'] \
                * (cp['モーション値']/100.0) \
                * (1.0 + 0.05*cp['百竜装飾品']['種系特効']) \
                * (1.0 + 0.1*cp['百竜装飾品']['やられ特効']) \
                * (1.0 + 0.05*cp['闇討ち'][1] + 0.1*cp['闇討ち'][2] + 0.2*cp['闇討ち'][3]) \
                * (1.0 + 0.05*cp['弾強化'][1] + 0.1*cp['弾強化'][2] + 0.2*cp['弾強化'][3]) \
                * (cp['物理肉質']/100.0) * cp['ビン補正'] \
                * (1.0 + 0.3*cp['にらみ撃ち']) \
                * (1.0 + 0.15*cp['矢強化']) \
                * (1.0 + 0.01*cp['射撃術'][1] + 0.02*cp['射撃術'][2] + 0.03*cp['射撃術'][3] + 0.04*cp['射撃術'][4]) \
                * (1.0 + (mdl.afr/100.0) * (1.25 + 0.05*mdl.x['超会心',1] + 0.1*mdl.x['超会心',2] + 0.15*mdl.x['超会心',3] - 1.0))
 

print('damage test:')

def test_damage_and_exit(input_dict):
    # 前回の計算結果の出力 (ダメージ寄与スキルのみ)

    mdlx = {dskill for dskill in list(damage_skill_set)}

    mdlx = {
        "攻撃":  [0] * 8,
        "見切り":  [0] * 8,
        "伏魔響命":  [0] * 4,
        "業鎧【修羅】":  [0] * 4,
        "火属性攻撃強化":  [0] * 6,
        "水属性攻撃強化":  [0] * 6,
        "氷属性攻撃強化":  [0] * 6,
        "雷属性攻撃強化":  [0] * 6,
        "龍属性攻撃強化":  [0] * 6,
        "挑戦者":  [0] * 6,
        "逆恨み":  [0] * 6,
        "龍気活性":  [0] * 6,
        "奮闘":  [0] * 4,
        "狂竜症【蝕】":  [0] * 4,
        "災禍転福":  [0] * 4,
        "連撃":  [0] * 4,
        "攻勢":  [0] * 4,
        "巧撃":  [0] * 4,
        "闇討ち":  [0] * 4,
        "フルチャージ":  [0] * 4,
        "逆襲":  [0] * 4,
        "死中に活":  [0] * 4,
        "弱点特効":  [0] * 4,
        "超会心":  [0] * 4,
        "弱点特効【属性】":  [0] * 4,
        "会心撃【属性】":  [0] * 4,
        "チャージマスター":  [0] * 4,
        "通常弾・連射矢強化":  [0] * 4,
        "散弾・拡散矢強化":  [0] * 4,
        "貫通弾・貫通矢強化":  [0] * 4,
        "渾身":  [0] * 4,
        "鋼殻の恩恵":  [0] * 3,
        "炎鱗の恩恵":  [0] * 3,
    }

    for key in input_dict:
        if key in damage_skill_set:
            # mdl.x[key,input_dict[key]] = True
            mdlx[key][input_dict[key]] = 1

    print('mdlx = ', mdlx)

    mdlafr = min(100.0, (cp['武器会心率'] + 15*cp['鋼龍の魂'] \
                    + 5*mdlx['見切り'][1] + 10*mdlx['見切り'][2] + 15*mdlx['見切り'][3] \
                    + 20*mdlx['見切り'][4] + 25*mdlx['見切り'][5] + 30*mdlx['見切り'][6] + 40*mdlx['見切り'][7] \
                    + 3*mdlx['挑戦者'][1] + 5*mdlx['挑戦者'][2] + 7*mdlx['挑戦者'][3] + 10*mdlx['挑戦者'][4] + 15*mdlx['挑戦者'][5] \
                    + 10*mdlx['奮闘'][1] + 15*mdlx['奮闘'][2] + 20*mdlx['奮闘'][3] \
                    + 15*cp['狂竜症【蝕】'][2] \
                    + cp['狂竜症【蝕】'][1] * (20*mdlx['狂竜症【蝕】'][1] + 25*mdlx['狂竜症【蝕】'][2] + 25*mdlx['狂竜症【蝕】'][3]) \
                    + 10*mdlx['攻勢'][2] + 20*mdlx['攻勢'][3] \
                    + 15*mdlx['弱点特効'][1] + 30*mdlx['弱点特効'][2] + 50*mdlx['弱点特効'][3] \
                    + 10*mdlx['渾身'][1] + 20*mdlx['渾身'][2] + 30*mdlx['渾身'][3] \
                    + 50*cp['アミキリアカネ'] \
                    + 30*cp['強化咆哮']))



    p_damage = (cp['武器倍率'] \
                    * (1.0 + 0.05*mdlx['龍気活性'][4] + 0.1*mdlx['龍気活性'][5]) \
                    * (1.0 + 0.05*mdlx['攻撃'][4] + 0.06*mdlx['攻撃'][5] + 0.08*mdlx['攻撃'][6] + 0.1*mdlx['攻撃'][7]) \
                    + 3*mdlx['攻撃'][1] + 6*mdlx['攻撃'][2] + 9*mdlx['攻撃'][3] + 7*mdlx['攻撃'][4] + 8*mdlx['攻撃'][5] + 9*mdlx['攻撃'][6] + 10*mdlx['攻撃'][7] \
                    + cp['SSW'][1] * (25*mdlx['伏魔響命'][1] + 30*mdlx['伏魔響命'][2] + 35*mdlx['伏魔響命'][3]) \
                    + cp['SSW'][0] * (15*mdlx['業鎧【修羅】'][1] + 25*mdlx['業鎧【修羅】'][2] + 35*mdlx['業鎧【修羅】'][3]) \
                    + 4*mdlx['挑戦者'][1] + 8*mdlx['挑戦者'][2] + 12*mdlx['挑戦者'][3] + 16*mdlx['挑戦者'][4] + 20*mdlx['挑戦者'][5] \
                    + 5*mdlx['逆恨み'][1] + 10*mdlx['逆恨み'][2] + 15*mdlx['逆恨み'][3] + 20*mdlx['逆恨み'][4] + 25*mdlx['逆恨み'][5] \
                    + cp['狂竜症【蝕】'][0] *(10*mdlx['狂竜症【蝕】'][1] + 15*mdlx['狂竜症【蝕】'][2] + 20*mdlx['狂竜症【蝕】'][3])\
                    + 12*mdlx['災禍転福'][1] + 15*mdlx['災禍転福'][2] + 18*mdlx['災禍転福'][3] \
                    + 8*mdlx['連撃'][1] + 9*mdlx['連撃'][2] + 10*mdlx['連撃'][3] \
                    + 10*mdlx['攻勢'][1] + 10*mdlx['攻勢'][2] + 15*mdlx['攻勢'][3] \
                    + 10*mdlx['巧撃'][1] + 15*mdlx['巧撃'][2] + 30*mdlx['巧撃'][3] \
                    + 5*mdlx['フルチャージ'][1] + 10*mdlx['フルチャージ'][2] + 20*mdlx['フルチャージ'][3] \
                    + 10*mdlx['逆襲'][1] + 15*mdlx['逆襲'][2] + 20*mdlx['逆襲'][3] \
                    + 5*mdlx['死中に活'][1] + 10*mdlx['死中に活'][2] + 20*mdlx['死中に活'][3] \
                    + 15*cp['劫血活性'][1] + 30*cp['劫血活性'][2] \
                    + cp['ヒトダマドリ']) \
                    * cp['溜め補正物理'] \
                    * (cp['モーション値']/100.0) \
                    * (1.0 + 0.05*cp['百竜装飾品特効乗算']) \
                    * (1.0 + 0.05*cp['闇討ち'][1] + 0.1*cp['闇討ち'][2] + 0.2*cp['闇討ち'][3]) \
                    * (1.0 + 0.05*cp['弾強化'][1] + 0.1*cp['弾強化'][2] + 0.2*cp['弾強化'][3]) \
                    * (cp['物理肉質']/100.0) * cp['ビン補正'] \
                    * (1.0 + (mdlafr/100.0) * (1.25 + 0.05*mdlx['超会心'][1] + 0.1*mdlx['超会心'][2] + 0.15*mdlx['超会心'][3] - 1.0))



    e_mul1 = (1 - cp['属性'][0]) * ((cp['武器属性値'] \
                    * (1.0 + 0.1*cp['劫血活性'][1] + 0.2*cp['劫血活性'][2]) \
                    * (1.0 + cp['SSW'][1] * (0.05*mdlx['業鎧【修羅】'][1] +  0.1*mdlx['業鎧【修羅】'][2] +  0.2*mdlx['業鎧【修羅】'][3])) \
                    * (1.0 + cp['属性'][1] * (0.05*mdlx['火属性攻撃強化'][3] +  0.1*mdlx['火属性攻撃強化'][4] +  0.2*mdlx['火属性攻撃強化'][5])) \
                    * (1.0 + cp['属性'][2] * (0.05*mdlx['水属性攻撃強化'][3] +  0.1*mdlx['水属性攻撃強化'][4] +  0.2*mdlx['水属性攻撃強化'][5])) \
                    * (1.0 + cp['属性'][3] * (0.05*mdlx['氷属性攻撃強化'][3] +  0.1*mdlx['氷属性攻撃強化'][4] +  0.2*mdlx['氷属性攻撃強化'][5])) \
                    * (1.0 + cp['属性'][4] * (0.05*mdlx['雷属性攻撃強化'][3] +  0.1*mdlx['雷属性攻撃強化'][4] +  0.2*mdlx['雷属性攻撃強化'][5])) \
                    * (1.0 + cp['属性'][5] * (0.05*mdlx['龍属性攻撃強化'][3] +  0.1*mdlx['龍属性攻撃強化'][4] +  0.2*mdlx['龍属性攻撃強化'][5])) \
                    * (1.0 + 0.1*mdlx['奮闘'][1] +  0.15*mdlx['奮闘'][2] +  0.2*mdlx['奮闘'][3]) \
                    * (1.0 + cp['属性'][2] * (0.05*mdlx['鋼殻の恩恵'][1] +  0.1*mdlx['鋼殻の恩恵'][2])) \
                    * (1.0 + cp['属性'][3] * (0.05*mdlx['鋼殻の恩恵'][1] +  0.1*mdlx['鋼殻の恩恵'][2])) \
                    * (1.0 + cp['属性'][1] * (0.05*mdlx['炎鱗の恩恵'][1] +  0.1*mdlx['炎鱗の恩恵'][2]))))
    
    e_add = e_mul1  + cp['SSW'][0] * (12*mdlx['伏魔響命'][1] + 15*mdlx['伏魔響命'][2] + 20*mdlx['伏魔響命'][3]) \
                    + cp['属性'][1] * (2*mdlx['火属性攻撃強化'][1] +  3*mdlx['火属性攻撃強化'][2] +  4*mdlx['火属性攻撃強化'][3] + 4*mdlx['火属性攻撃強化'][4] +  4*mdlx['火属性攻撃強化'][5]) \
                    + cp['属性'][2] * (2*mdlx['水属性攻撃強化'][1] +  3*mdlx['水属性攻撃強化'][2] +  4*mdlx['水属性攻撃強化'][3] + 4*mdlx['水属性攻撃強化'][4] +  4*mdlx['水属性攻撃強化'][5]) \
                    + cp['属性'][3] * (2*mdlx['氷属性攻撃強化'][1] +  3*mdlx['氷属性攻撃強化'][2] +  4*mdlx['氷属性攻撃強化'][3] + 4*mdlx['氷属性攻撃強化'][4] +  4*mdlx['氷属性攻撃強化'][5]) \
                    + cp['属性'][4] * (2*mdlx['雷属性攻撃強化'][1] +  3*mdlx['雷属性攻撃強化'][2] +  4*mdlx['雷属性攻撃強化'][3] + 4*mdlx['雷属性攻撃強化'][4] +  4*mdlx['雷属性攻撃強化'][5]) \
                    + cp['属性'][5] * (2*mdlx['龍属性攻撃強化'][1] +  3*mdlx['龍属性攻撃強化'][2] +  4*mdlx['龍属性攻撃強化'][3] + 4*mdlx['龍属性攻撃強化'][4] +  4*mdlx['龍属性攻撃強化'][5]) \
                    + cp['狂竜症【蝕】'][0] * (5*mdlx['狂竜症【蝕】'][1] + 7*mdlx['狂竜症【蝕】'][2] + 10*mdlx['狂竜症【蝕】'][3]) \
                    + 2*mdlx['災禍転福'][1] + 3*mdlx['災禍転福'][2] + 4*mdlx['災禍転福'][3] \
                    + 6*mdlx['連撃'][1] + 8*mdlx['連撃'][2] + 10*mdlx['連撃'][3] 

    e_mul2 = e_add *  (cp['溜め補正属性'] * cp['属性肉質'] / 100.0 \
                    * (1.0 + 0.1*mdlx['弱点特効【属性】'][1] + 0.125*mdlx['弱点特効【属性】'][2] + 0.15*mdlx['弱点特効【属性】'][3]) \
                    * (1.0 + 0.05*mdlx['チャージマスター'][1] + 0.1*mdlx['チャージマスター'][2] + 0.15*mdlx['チャージマスター'][3]) \
                    * cp['怒り補正'] \
                    * (1.0 + (mdlafr/100.0) * (1.0 + 0.05*mdlx['会心撃【属性】'][1] + 0.1*mdlx['会心撃【属性】'][2] + 0.15*mdlx['会心撃【属性】'][3] - 1.0)))




    e_damage =  (1 - cp['属性'][0]) * ((cp['武器属性値'] \
                    * (1.0 + 0.1*cp['劫血活性'][1] + 0.2*cp['劫血活性'][2]) \
                    * cp['SSW'][1] * (1.0 + 0.05*mdlx['業鎧【修羅】'][1] +  0.1*mdlx['業鎧【修羅】'][2] +  0.2*mdlx['業鎧【修羅】'][3]) \
                    * (1.0 + cp['属性'][1] * (0.05*mdlx['火属性攻撃強化'][3] +  0.1*mdlx['火属性攻撃強化'][4] +  0.2*mdlx['火属性攻撃強化'][5])) \
                    * (1.0 + cp['属性'][2] * (0.05*mdlx['水属性攻撃強化'][3] +  0.1*mdlx['水属性攻撃強化'][4] +  0.2*mdlx['水属性攻撃強化'][5])) \
                    * (1.0 + cp['属性'][3] * (0.05*mdlx['氷属性攻撃強化'][3] +  0.1*mdlx['氷属性攻撃強化'][4] +  0.2*mdlx['氷属性攻撃強化'][5])) \
                    * (1.0 + cp['属性'][4] * (0.05*mdlx['雷属性攻撃強化'][3] +  0.1*mdlx['雷属性攻撃強化'][4] +  0.2*mdlx['雷属性攻撃強化'][5])) \
                    * (1.0 + cp['属性'][5] * (0.05*mdlx['龍属性攻撃強化'][3] +  0.1*mdlx['龍属性攻撃強化'][4] +  0.2*mdlx['龍属性攻撃強化'][5])) \
                    * (1.0 + 0.1*mdlx['奮闘'][1] +  0.15*mdlx['奮闘'][2] +  0.2*mdlx['奮闘'][3]) \
                    * (1.0 + cp['属性'][2] * (0.05*mdlx['鋼殻の恩恵'][1] +  0.1*mdlx['鋼殻の恩恵'][2])) \
                    * (1.0 + cp['属性'][3] * (0.05*mdlx['鋼殻の恩恵'][1] +  0.1*mdlx['鋼殻の恩恵'][2])) \
                    * (1.0 + cp['属性'][1] * (0.05*mdlx['炎鱗の恩恵'][1] +  0.1*mdlx['炎鱗の恩恵'][2]))) \
                    + cp['SSW'][0] * (12*mdlx['伏魔響命'][1] + 15*mdlx['伏魔響命'][2] + 20*mdlx['伏魔響命'][3]) \
                    + cp['属性'][1] * (2*mdlx['火属性攻撃強化'][1] +  3*mdlx['火属性攻撃強化'][2] +  4*mdlx['火属性攻撃強化'][3] + 4*mdlx['火属性攻撃強化'][4] +  4*mdlx['火属性攻撃強化'][5]) \
                    + cp['属性'][2] * (2*mdlx['水属性攻撃強化'][1] +  3*mdlx['水属性攻撃強化'][2] +  4*mdlx['水属性攻撃強化'][3] + 4*mdlx['水属性攻撃強化'][4] +  4*mdlx['水属性攻撃強化'][5]) \
                    + cp['属性'][3] * (2*mdlx['氷属性攻撃強化'][1] +  3*mdlx['氷属性攻撃強化'][2] +  4*mdlx['氷属性攻撃強化'][3] + 4*mdlx['氷属性攻撃強化'][4] +  4*mdlx['氷属性攻撃強化'][5]) \
                    + cp['属性'][4] * (2*mdlx['雷属性攻撃強化'][1] +  3*mdlx['雷属性攻撃強化'][2] +  4*mdlx['雷属性攻撃強化'][3] + 4*mdlx['雷属性攻撃強化'][4] +  4*mdlx['雷属性攻撃強化'][5]) \
                    + cp['属性'][5] * (2*mdlx['龍属性攻撃強化'][1] +  3*mdlx['龍属性攻撃強化'][2] +  4*mdlx['龍属性攻撃強化'][3] + 4*mdlx['龍属性攻撃強化'][4] +  4*mdlx['龍属性攻撃強化'][5]) \
                    + cp['狂竜症【蝕】'][0] * (5*mdlx['狂竜症【蝕】'][1] + 7*mdlx['狂竜症【蝕】'][2] + 10*mdlx['狂竜症【蝕】'][3]) \
                    + 2*mdlx['災禍転福'][1] + 3*mdlx['災禍転福'][2] + 4*mdlx['災禍転福'][3] \
                    + 6*mdlx['連撃'][1] + 8*mdlx['連撃'][2] + 10*mdlx['連撃'][3]) \
                    * (cp['溜め補正属性'] * cp['属性肉質'] / 100.0 \
                    * (1.0 + 0.1*mdlx['弱点特効【属性】'][1] + 0.125*mdlx['弱点特効【属性】'][2] + 0.15*mdlx['弱点特効【属性】'][3]) \
                    * (1.0 + 0.05*mdlx['チャージマスター'][1] + 0.1*mdlx['チャージマスター'][2] + 0.15*mdlx['チャージマスター'][3]) \
                    * cp['怒り補正'] \
                    * (1.0 + (mdlafr/100.0) * (1.0 + 0.05*mdlx['会心撃【属性】'][1] + 0.1*mdlx['会心撃【属性】'][2] + 0.15*mdlx['会心撃【属性】'][3] - 1.0)))



    print('P_damage = ', p_damage)
    print('e_mul_top = ', (1 - cp['属性'][0]) * ((cp['武器属性値'])) * (1.0 + 0.1*cp['劫血活性'][1] + 0.2*cp['劫血活性'][2]))
    print('e_mul1 = ', e_mul1)

    print('e_add = ', e_add)
    print('e_mul2 = ', e_mul2)

    print('E_damage = ', e_damage)

    print('damage test done. EXIT')
    exit(0)

# test_damage_and_exit(
#     # ここに前回の計算結果を入力して検証
#     {'会心撃【属性】': 1, '伏魔響命': 3, 'チャージマスター': 3, '弱点特効【属性】': 1, '火属性攻撃強化': 3, '災禍転福': 3, '狂竜症【蝕】': 1, '連撃': 3, '弾導強化': 1, '装填速度': 2, '弓溜め段階解放': 1, '通常弾・連射矢強化': 3}
# )



# mdl.OBJ = Objective(rule=objective, sense=maximize)
mdl.OBJ = Objective(rule=objective_physics_only, sense=maximize)
# mdl.OBJ = Objective(rule=objective_nonlinear, sense=maximize)


# symbolic_solver_labels を有効化して scip solver に解かせれば
# 対話型シェルの display solution コマンドや
# C/C++ API の SCIP_CALL( SCIPprintSol(scip, SCIPgetBestSol(scip), NULL, FALSE) ); などでスキル名等の情報込みの変数を見ることができる
mdl.write("dmax_sample_p.nl", io_options={'symbolic_solver_labels': True})
compmap = mdl.component_map()

compobj = mdl.component_objects()
print(compobj)

# # 変数の一覧を取得できている?
# comp_itr = mdl.component_data_iterindex()
# for key in comp_itr:
#     print(key)

# comp_id = mdl.id_index_map()
# for key in comp_id:
#     print(key)



# help(compmap)
# for key in compmap:
#     print(key, compmap[key])
#     for key2 in compmap[key]:
#         print(key2)
exit(0)

# help(mdl)

# help(SolverFactory("scip"))


opt = SolverFactory("scip") # solver を scip に変更 (scipamplでは動作しなかった)
result = opt.solve(mdl, options={'lp/threads':7, 'parallel/minnthreads':7, 'parallel/maxnthreads':7, }, tee=True)
mdl.display()

# 以下は全て結果の出力用
print('\n\nresult: \n', result)
print('variables:')
print('    objective:', mdl.OBJ())

for v in mdl.component_data_objects(ctype=Var):
    if v.value != 0:
        if 'x[' in v.name and ',0' in v.name:
            continue
        print(f"{v.name=}, {v.lb=}, {v.value=}, {v.ub=}")


print("\n\nSkill Result:")
result_skill_dict = {}
for v in mdl.component_data_objects(ctype=Var):
    if round(v.value) != 0:
        if 'x[' in v.name and ',0' in v.name:
            continue
        if 'q[' in v.name:
            continue
        if 'afr' in v.name:
            continue
        skill_name = v.name[v.name.find('[')+1:v.name.find(',')]
        skill_level = int(v.name[v.name.find(',')+1:v.name.find(']')])
        result_skill_dict[skill_name] = skill_level

for rskill in required_skills:
    result_skill_dict[rskill] = required_skills[rskill]

print(result_skill_dict)

nakisim_url = 'https://mhrise.wiki-db.com/sim/#skills='
for key in result_skill_dict:
    nakisim_url += '%2C' + key + 'Lv' + str(result_skill_dict[key])
nakisim_url += '&s=2&e=1&v=10&g=13&w=&ws=&d=0&rf=-100&rw=-100&rt=-100&ri=-100&rd=-100&l=200'

nakisim_url = nakisim_url.replace('#skills=%2C', '#skills=')

print("\n\nprint damage skills in naki-sim url format")
print("\n  :", nakisim_url)
print("\n  :", urllib.parse.quote(nakisim_url, safe='Lv%2Chttps://mhrise.wiki-db.com/sim/#skills=&s=2&e=1&v=10&g=13&w=&ws=&d=0&rf=-100&rw=-100&rt=-100&ri=-100&rd=-100&l=200'))

