### 主要なファイル説明
| ファイル名 | 説明 |
| ---- | ---- |
| dmax | dmax 本体 |
| dmax_skill_sim_scip.py | dmax のプロトタイプ |
| skill-simu-scip.py | Pyomo+SCIPによるスキルシミュレータの実装 |
| damage_expression_full.py | 完全なダメージ計算式の検証用 |
| damage_expression.py | 簡易的なダメージ計算式の検証用 |
| equipdata.py | 装備(防具･装飾品)のデータ |

- equipdata.py は memo/monster-hunter/mhrs-sim-data で作成

### これはなに?
MHR:Sunbreak というゲームにおいて ｢ダメージを最大化する装備を自動で見つけてくれるツール｣ です。D-max(仮称) です。

### 何がうれしいの?
- 最大ダメージであることが保証されます
- スキルシミュとダメシミュを交互に使って最大ダメージを探索する作業が自動化されます

### どういう仕組み?
- ダメージを最大化するという最適化問題を定式化し、整数計画ソルバーであるSCIPに解いてもらいます
- ダメージ計算式は非線形の目的関数となるため、非線形整数計画問題として定式化出来ます
- SCIPは非線形整数計画問題に対応しているため解けます
- 以下の2つのアプローチでは組合せ爆発により非常に時間がかかったり有限時間に解けなかったりします
  - 全てのスキルの組み合せを全探索し、スキルシミュレータに解かせる
  - 乗数部分を展開して線形の整数計画問題として定式化する

### 実装状況
- 2022/01/31 簡易的な弓のダメージ計算式の最大化問題を解けます
- 2022/02/01 完全な式を実装 (dmax.py)
  - スキルandスキル や スキルandダメージ の制約は未実装のものあり (フルチャと逆恨みが共存するなど)
  - 243.24秒 で解けた
    - 弾強化3のみの条件指定 で 物理+属性 の完全なダメージ計算式を目的関数とした場合
    - データ入力は最低限 (護石･傀異錬成なし)
    - ダメージ計算式がずれているので要修正





### SCIP 環境構築 (wsl+Ubuntu20.04)
この文章は memo リポジトリからコピーしてきたもの

1. 公式ページの Download へ移動して version:8.03 OS:Linux を選択
https://www.scipopt.org/download.php?fname=scipoptsuite-8.0.3.tgz

2. scipoptsuite-8.0.3.tgz をクリック
3. 必要な項目を埋めて Start Download を押すと scipoptsuite-8.0.3.tgz がダウンロードされる
4. wsl配下のフォルダに scipoptsuite-8.0.3.tgz を移動
5. 解凍 & make
   - 参考 https://www.scipopt.org/doc-3.2.0/html/INSTALL.php
   ```
   Compiling SCIP directly can be done as follows:

    1) unpack the tarball "tar xvzf scip-x.y.z.tgz"
    2) change into the directory "cd scip-x.y.z"
    3) start compiling SCIP "make"
    3) (recommended) check your SCIP installation "make test"
    4) (optional) install the header, libraries, and binary, e.g.,
      "make install INSTALLDIR="/usr/local/"
   ```
   - wsl+ubuntu20.04 で環境構築
   ```sh
   $ pwd
   /home/hoge/wsl_work

   cp /mnt/c/User/neong/Download/scipoptsuite-8.0.3.tgz .
   cd scipoptsuite-8.0.3.tgz

   # make を実行するの必要なパッケージを集める
   sudo apt update
   sudo apt install libboost-dev # boost をインストール

   # GMP に必要なパッケージをインストール
   sudo apt install g++ m4 zlib1g-dev make p7zip # 不要かも
   sudo apt install libgmp-dev # gmp をインストール
   sudo apt install -y libreadline-dev # readline をインストール

   # make実行
   make
   # テスト
   make test
   # パスを通す
   sudo make install INSTALLDIR="/usr/local/"

   scip # scip シェルが起動する
   ```
6. Pyomo + Python + SCIP
  - 参考 [最適化ソルバーSCIP，モデリング言語Pyomoを使ってPythonで最適化問題を解いてみた](https://gadgetlunatic.com/post/scip-python-optimization/)
  ```sh
  pip install pyomo
  ```
  警告が出たのでパスを通しておく vi ~/.bashrc で開いて
  ```sh
  export PATH="$PATH:$HOME/.local/bin"
  ```

  ファイル scip-sample.py を作成して 以下を記述 (ソルバーの指定部分を一部改変)
  - ファイル保存場所: /home/hoge/wsl_work/scip-sample/scip-sample.py
  ```py
  from pyomo.environ import *
  from pyomo.opt import SolverFactory

  Model = ConcreteModel("Sample")


  Model.x1 = Var(within=NonNegativeReals)
  Model.x2 = Var(within=NonNegativeReals)
  Model.x3 = Var(within=NonNegativeReals)


  def const_1(model):
      return 2 * Model.x1 + Model.x2 + Model.x3 <= 60


  def const_2(model):
      return Model.x1 + 2 * Model.x2 + Model.x3 <= 60


  def const_3(model):
      return Model.x3 <= 30


  Model.const_1 = Constraint(rule=const_1)
  Model.const_2 = Constraint(rule=const_2)
  Model.const_3 = Constraint(rule=const_3)


  def objective(model):
      return 15 * Model.x1 + 18 * Model.x2 + 30 * Model.x3


  Model.value = Objective(rule=objective, sense=maximize)

  opt = SolverFactory("scip")  # solver を scipampl から scip に変更
  result = opt.solve(Model, tee=True)
  Model.display()
  ```

  ```
  $ python3 scip-sample.py
  SCIP version 8.0.3 [precision: 8 byte] [memory: block] [mode: optimized] [LP solver: Soplex 6.0.3] [GitHash: 62fab8a2e3]
  Copyright (C) 2002-2022 Konrad-Zuse-Zentrum fuer Informationstechnik Berlin (ZIB)

  External libraries:
    Readline 8.0         GNU library for command line editing (gnu.org/s/readline)
    Soplex 6.0.3         Linear Programming Solver developed at Zuse Institute Berlin (soplex.zib.de) [GitHash: f900e3d0]
    CppAD 20180000.0     Algorithmic Differentiation of C++ algorithms developed by B. Bell (github.com/coin-or/CppAD)
    ZLIB 1.2.11          General purpose compression library by J. Gailly and M. Adler (zlib.net)
    GMP 6.2.0            GNU Multiple Precision Arithmetic Library developed by T. Granlund (gmplib.org)
    AMPL/MP 4e2d45c4     AMPL .nl file reader library (github.com/ampl/mp)
    bliss 0.77           Computing Graph Automorphism Groups by T. Junttila and P. Kaski (www.tcs.hut.fi/Software/bliss/)

  user parameter file <scip.set> not found - using default parameters
  read problem </tmp/tmp2157h70y.pyomo.nl>
  ============

  original problem has 3 variables (0 bin, 0 int, 0 impl, 3 cont) and 3 constraints

  solve problem
  =============

  feasible solution found by trivial heuristic after 0.0 seconds, objective value 0.000000e+00
  presolving:
  (round 1, fast)       0 del vars, 1 del conss, 0 add conss, 5 chg bounds, 0 chg sides, 0 chg coeffs, 0 upgd conss, 0 impls, 0 clqs
    (0.0s) symmetry computation started: requiring (bin +, int +, cont +), (fixed: bin -, int -, cont -)
    (0.0s) no symmetry present
  presolving (2 rounds: 2 fast, 1 medium, 1 exhaustive):
  0 deleted vars, 1 deleted constraints, 0 added constraints, 5 tightened bounds, 0 added holes, 0 changed sides, 0 changed coefficients
  0 implications, 0 cliques
  presolved problem has 3 variables (0 bin, 0 int, 0 impl, 3 cont) and 2 constraints
        2 constraints of type <linear>
  Presolving Time: 0.00
  transformed 1/1 original solutions to the transformed problem space

  time | node  | left  |LP iter|LP it/n|mem/heur|mdpt |vars |cons |rows |cuts |sepa|confs|strbr|  dualbound   | primalbound  |  gap   | compl.
  * 0.0s|     1 |     0 |     2 |     - |    LP  |   0 |   3 |   2 |   2 |   0 |  0 |   0 |   0 | 1.230000e+03 | 1.230000e+03 |   0.00%| unknown
    0.0s|     1 |     0 |     2 |     - |   591k |   0 |   3 |   2 |   2 |   0 |  0 |   0 |   0 | 1.230000e+03 | 1.230000e+03 |   0.00%| unknown

  SCIP Status        : problem is solved [optimal solution found]
  Solving Time (sec) : 0.00
  Solving Nodes      : 1
  Primal Bound       : +1.23000000000000e+03 (2 solutions)
  Dual Bound         : +1.23000000000000e+03
  Gap                : 0.00 %
  Model Sample

    Variables:
      x1 : Size=1, Index=None
          Key  : Lower : Value : Upper : Fixed : Stale : Domain
          None :     0 :  10.0 :  None : False : False : NonNegativeReals
      x2 : Size=1, Index=None
          Key  : Lower : Value : Upper : Fixed : Stale : Domain
          None :     0 :  10.0 :  None : False : False : NonNegativeReals
      x3 : Size=1, Index=None
          Key  : Lower : Value : Upper : Fixed : Stale : Domain
          None :     0 :  30.0 :  None : False : False : NonNegativeReals

    Objectives:
      value : Size=1, Index=None, Active=True
          Key  : Active : Value
          None :   True : 1230.0

    Constraints:
      const_1 : Size=1
          Key  : Lower : Body : Upper
          None :  None : 60.0 :  60.0
      const_2 : Size=1
          Key  : Lower : Body : Upper
          None :  None : 60.0 :  60.0
      const_3 : Size=1
          Key  : Lower : Body : Upper
          None :  None : 30.0 :  30.0
  ```

  とけたっぽい
