# ダメージ計算式の検証用ファイル

# skill parameter 入力する値
sp = {
    "攻撃": 7,
    "伏魔響命・朱": 0,
    "伏魔響命・青": 2,
    "逆恨み": 3,
    "見切り": 6,
    "挑戦者": 1,
    "奮闘": 2,
    "超会心": 2,
}

sp_max = {
    "攻撃": 7,
    "伏魔響命・朱": 3,
    "伏魔響命・青": 3,
    "逆恨み": 5,
    "見切り": 7,
    "挑戦者": 5,
    "奮闘": 3,
    "超会心": 3,
}



# binary parameter
bp = {}

for skill in sp:
    bp[skill] = [0] * (sp_max[skill] + 1)
    bp[skill][sp[skill]] = 1

# constant parameter

cp = {
    "武器倍率": 300.0,
    "溜め補正物理": 1.35,
    "モーション値": 11.0,
    "肉質": 55.0,
    "ビン補正": 1.35,
    "武器会心率": 0.0,
}

print('sp:\n', sp)
print('sp_max:\n', sp_max)
print('bp:\n', bp)
print('cp:\n', cp)



# ((武器倍率) * (攻撃スキル) + (攻撃スキル加算 + 伏魔響命青 + 逆恨み + 挑戦者)) * (物理溜め補正) * (モーション値 / 100) *(肉質/100) * (強撃ビン補正) *(1.0 + (会心補正 - 1.0) * (武器会心率 + 見切り + 挑戦者 + 奮闘))

MUL1 = cp['武器倍率'] * (1.0 + 0.05*bp['攻撃'][4] + 0.06*bp['攻撃'][5] + 0.08*bp['攻撃'][6] + 0.1*bp['攻撃'][7])

ADD = MUL1 + 3*bp['攻撃'][1] + 6*bp['攻撃'][2] + 9*bp['攻撃'][3] + 7*bp['攻撃'][4] + 8*bp['攻撃'][5] + 9*bp['攻撃'][6] + 10*bp['攻撃'][7]\
      + 25*bp['伏魔響命・青'][1] + 30*bp['伏魔響命・青'][2] + 35*bp['伏魔響命・青'][3]\
      + 5*bp['逆恨み'][1] + 10*bp['逆恨み'][2] + 15*bp['逆恨み'][3] + 20*bp['逆恨み'][4] + 25*bp['逆恨み'][5]\
      + 4*bp['挑戦者'][1] + 8*bp['挑戦者'][2] + 12*bp['挑戦者'][3] + 16*bp['挑戦者'][4] + 20*bp['挑戦者'][5]\

AFFR = (min(100.0, cp['武器会心率'] + 5*bp['見切り'][1] + 10*bp['見切り'][2] + 15*bp['見切り'][3] + 20*bp['見切り'][4] + 25*bp['見切り'][5] + 30*bp['見切り'][6] + 40*bp['見切り'][7]\
                      + 10*bp['奮闘'][1] + 15*bp['奮闘'][2] + 20*bp['奮闘'][3]\
                      + 3*bp['挑戦者'][1] + 5*bp['挑戦者'][2] + 7*bp['挑戦者'][3] + 10*bp['挑戦者'][4] + 15*bp['挑戦者'][5]))/100.0


MUL2 = ADD * cp['溜め補正物理'] * (cp['モーション値']/100.0) *  (cp['肉質']/100.0) * cp['ビン補正']\
       * (1.0 + (AFFR) * (1.25 + 0.05*bp['超会心'][1] + 0.1*bp['超会心'][2] + 0.15*bp['超会心'][3] - 1.0))

print(MUL1)
print(ADD)
print(AFFR)
print(MUL2)




# damage = (300 * (1.0 *(model.AB0 + model.AB1 + model.AB2 + model.AB3) + 1.05 * model.AB4 + 1.06 * model.AB5 + 1.08 * model.AB6 + 1.1 * model.AB7) + 3 * model.AB1 + 6 * model.AB2 + 9 * model.AB3 + 7 * model.AB4 + 8 * model.AB5 + 9 * model.AB6 + 10 * model.AB7 + 15 * model.FUKUMA_AO1 + 20 * model.FUKUMA_AO2 + 25 * model.FUKUMA_AO3 + 4 * model.CHOUSENSHA1 + 8 * model.CHOUSENSHA2 + 12 * model.CHOUSENSHA3 + 16 * model.CHOUSENSHA4 + 20 * model.CHOUSENSHA5 + 5 * model.SAKAURAMI1 + 10 * model.SAKAURAMI2 + 15 * model.SAKAURAMI3 + 20 * model.SAKAURAMI4 + 25 * model.SAKAURAMI5) * (1.35) * (11/100) * (55/100) * (1.35) * (1 + (1.25 * model.CHOUKAISIN0 + 1.30 * model.CHOUKAISIN1 + 1.35 * model.CHOUKAISIN2 + 1.4 * model.CHOUKAISIN3 -1.0) * ((0 + 5 * model.MIKIRI1 + 10 * model.MIKIRI2 + 15 * model.MIKIRI3 + 20 * model.MIKIRI4 + 25 * model.MIKIRI5 + 30 * model.MIKIRI6 + 40 * model.MIKIRI7 + 3 * model.CHOUSENSHA1 + 5 * model.CHOUSENSHA2 + 7 * model.CHOUSENSHA3 + 10 * model.CHOUSENSHA4 + 15 * model.CHOUSENSHA5 + 10 * model.HUNTOU1 + 15 *model.HUNTOU2 + 20 * model.HUNTOU3)/100) )

