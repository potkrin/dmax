### 主要なファイル説明
| ファイル名 | 説明 |
| ---- | ---- |
| dmax.py | dmax 本体 (非線形目的関数を制約条件に変更したバージョン) |
| dmax_nonlinear_obj.py | dmax 本体 (目的関数が非線形なままのバージョン) |
| dmax_skill_sim_scip.py | dmax のプロトタイプ |
| skill-simu-scip.py | Pyomo+SCIPによるスキルシミュレータの実装 |
| damage_expression_full.py | 完全なダメージ計算式の検証用 |
| damage_expression.py | 簡易的なダメージ計算式の検証用 |
| equipdata.py | 装備(防具･装飾品)のデータ |
| *.nl | 非線形整数計画問題の出力ファイル. 対話シェルやC/C++APIでSCIPに読み込ませることができる |

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



### SCIPをマルチスレッドで実行する
1. scip の make 時に TPI=tny オプションを指定する
  ```sh
  # tar ファイルを展開したフォルダに移動
  $ pwd
  /home/hoge/wsl_work/scipoptsuite-8.0.3

  # TPI=tny オプションを指定して make を実行
  $ make TPI=tny

  $ ls -l scip/bin/
  合計 21152
  lrwxrwxrwx 1 root root       41  2月  5 06:02 scip -> scip-8.0.3.linux.x86_64.gnu.opt.spx2.none # シンボリックリンク
  # ~.tny がマルチスレッド非対応
  -rwxr-xr-x 1 root root 10255552  2月  5 06:02 scip-8.0.3.linux.x86_64.gnu.opt.spx2.none
  # ~.tny がマルチスレッド対応版
  -rwxr-xr-x 1 hoge hoge 11402416  2月  5 05:58 scip-8.0.3.linux.x86_64.gnu.opt.spx2.tny
  lrwxrwxrwx 1 hoge hoge       41  2月  5 06:01 scip.linux.x86_64.gnu.opt.spx2.none -> scip-8.0.3.linux.x86_64.gnu.opt.spx2.none
  lrwxrwxrwx 1 hoge hoge       40  2月  2 20:59 scip.linux.x86_64.gnu.opt.spx2.tny -> scip-8.0.3.linux.x86_64.gnu.opt.spx2.tny
  ```

2. sudo make install を実行
  ```sh
  sudo make install INSTALLDIR="/usr/local"
  ```
  このとき 既に別の設定の SCIP をインストール済みの場合は マルチスレッド対応バージョンがパスに指定されない

3. マルチスレッド対応版をパスに指定する
  ```sh
  # 古いバイナリとシンボリックリンクを削除
  $ sudo rm /usr/local/bin/scip # none シンボリックリンク への シンボリックリンク
  $ sudo rm /usr/local/bin/scip.linux.x86_64.gnu.opt.spx2.none # シンボリックリンク
  $ sudo rm /usr/local/bin/scip-8.0.3.linux.x86_64.gnu.opt.spx2.none # 並列未対応のバイナリ

  # make で作成した 並列対応バイナリ を /usr/local/bin にコピー
  $ sudo cp ~/wsl_work/scipoptsuite-8.0.3/scip/bin/scip-8.0.3.linux.x86_64.gnu.opt.spx2.tny /usr/local/bin/
  # シンボリックリンクを作成
  $ sudo ln -s /usr/local/bin/scip-8.0.3.linux.x86_64.gnu.opt.spx2.tny /usr/local/bin/scip.linux.x86_64.gnu.opt.spx2.tny
  $ sudo ln -s /usr/local/bin/scip.linux.x86_64.gnu.opt.spx2.tny /usr/local/bin/scip

  # 最終状態
  $ ls -l /usr/local/bin/
  合計 39804
  lrwxrwxrwx 1 root root       49  2月  5 06:31 scip -> /usr/local/bin/scip.linux.x86_64.gnu.opt.spx2.tny
  -rwxr-xr-x 1 root root 11402416  2月  5 06:28 scip-8.0.3.linux.x86_64.gnu.opt.spx2.tny
  lrwxrwxrwx 1 root root       55  2月  5 06:30 scip.linux.x86_64.gnu.opt.spx2.tny -> /usr/local/bin/scip-8.0.3.linux.x86_64.gnu.opt.spx2.tny
  -rwxr-xr-x 1 root root  9783096  1月 29 03:30 soplex
  -rwxr-xr-x 1 root root  9783096  1月 29 03:30 soplex-6.0.3.linux.x86_64.gnu.opt
  -rwxr-xr-x 1 root root  9783096  1月 29 03:30 soplex.linux.x86_64.gnu.opt
  ```

4. scip 対話シェルを開いて 外部ライブラリに TinyCThread があることを確認
  ```sh
  $ scip
  SCIP version 8.0.3 [precision: 8 byte] [memory: block] [mode: optimized] [LP solver: Soplex 6.0.3] [GitHash: 62fab8a2e3]
  Copyright (C) 2002-2022 Konrad-Zuse-Zentrum fuer Informationstechnik Berlin (ZIB)

  External libraries:
    ... 略 ...
    TinyCThread          Small, portable implementation of the C11 threads API (tinycthread.github.io) # マルチスレッド対応

  user parameter file <scip.set> not found - using default parameters

  SCIP>
  ```

5. scip 対話シェルでのマルチスレッド実行
   ```sh
   SCIP> set save setting.set # 現在のパラメータをファイル setting.set に保存
   ```

6. setting.set ファイルでパラメータ設定
  以下のパラメータを設定
  ```sh
  # number of threads used for solving the LP (0: automatic)
  # [type: int, advanced: TRUE, range: [0,64], default: 0]
  lp/threads = 12

  # the minimum number of threads used during parallel solve
  # [type: int, advanced: FALSE, range: [0,64], default: 1]
  parallel/minnthreads = 8

  # the maximum number of threads used during parallel solve
  # [type: int, advanced: FALSE, range: [0,64], default: 8]
  parallel/maxnthreads = 12
  ```

7. scip 対話シェルで設定ファイルを読み込んで concurrentopt コマンドを叩く
  ```sh
  SCIP> set load setting.set
  loaded parameter file <setting.set>

  # 問題ファイル foo.nl の読み込み
  SCIP> read foo.nl
  read problem <foo.nl>
  ============

  original problem has 1993 variables (205 bin, 1787 int, 0 impl, 1 cont) and 88 constraints

  # 並列最適化実行
  SCIP> concurrentopt 

  # 逐次実行
  SCIP> optimize # opt でもいける
  ```
  - 同一問題ファイルで逐次とマルチスレッドを比較した結果
    - スレッド数 1: Solving Time (sec) : 650.61
    - スレッド数 2: Solving Time (sec) : 551.16
    - スレッド数 4: Solving Time (sec) : 76.84
    - スレッド数 6: Solving Time (sec) : 83.92
    - スレッド数 8: Solving Time (sec) : 83.41
    - スレッド数 8: Solving Time (sec) : 99.96
      ``sh
      lp/threads = 6 # スレッド数6の場合 全て6
      parallel/minnthreads = 6
      parallel/maxnthreads = 6
      ```



 
  

8. 補足: 問題ファイル foo.nl の作り方
  ```py
  # dmax.py
  https://github.com/Pyomo/pyomo/blob/main/pyomo/repn/plugins/nl_writer.py
  # mdl.OBJ = Objective(rule=objective, sense=maximize)
  # モデル作成
  mdl = ConcreteModel(name="dmax model", doc="model for solving damage optimization problem") # name doc は省略可
  # 目的関数などの設定
  mdl.OBJ = Objective(rule=objective_physics_only, sense=maximize)

  # モデルを .nl ファイルとして出力
  # io_options は 変数情報を .nl ファイルに出力するために必要
  # この変数情報がないと 対話型シェル や C/C++API から scip で解いた結果を表示するときに結果を読み解けなくて詰む
  # (スキルA:7 などではなく c10:7 などと表示されてしまうため結果が分からない)
  mdl.write("dmax_sample_p.nl", io_options={'symbolic_solver_labels': True})
  ```



### C/C++ API から .nl ファイルを読み込む方法
- application sample: Coloring : /home/hoge/wsl_work/scipoptsuite-8.0.3/scip/applications/Coloring/src/main.c
  ```c
  SCIP_CALL( SCIPprocessShellArguments(scip, argc, argv, defaultsetname) );
  ```
- SCIPソルバに .nl ファイルの問題を読み込ませている箇所
  - /home/hoge/wsl_work/scipoptsuite-8.0.3/scip/src/scip/scipshell.c
    ```c
    /* AMPL calls solver with file without .nl extension, but others (Pyomo) may not
    * so add .nl only if not already present
    */
    nlfilenamelen = strlen(nlfilename);
    if( nlfilenamelen > 3 && strcmp(nlfilename + (nlfilenamelen-3), ".nl") == 0 )
      (void) SCIPsnprintf(fullnlfilename, SCIP_MAXSTRLEN, "%s", nlfilename);
    else
      (void) SCIPsnprintf(fullnlfilename, SCIP_MAXSTRLEN, "%s.nl", nlfilename);
    SCIPinfoMessage(scip, NULL, "read problem <%s>\n", fullnlfilename);
    SCIPinfoMessage(scip, NULL, "============\n\n");

    SCIP_CALL( SCIPreadProb(scip, fullnlfilename, "nl") );

    SCIPinfoMessage(scip, NULL, "\nsolve problem\n");
    SCIPinfoMessage(scip, NULL, "=============\n\n");

    SCIP_CALL( SCIPsolve(scip) );
  ```

- SCIPを静的リンクして C/C++ コードから .nl ファイルを読み込んでソルバに解かせることができた
  1. 次のコードに 上記スニペットを挿入 
    - ソースコード: scipoptsuite-8.0.3/scip/examples/CallableLibrary/src/brachistochrone.c
  2. make コマンドを実行
    ```sh
    $ pwd
    /home/hoge/wsl_work/scipoptsuite-8.0.3/scip/examples/CallableLibrary

    # example の make の前に SCIP の make が完了している必要がある
    $ ls -l /home/hoge/wsl_work/scipoptsuite-8.0.3/scip/bin/
    合計 22256
    lrwxrwxrwx 1 hoge hoge       41  2月  6 23:46 scip -> scip-8.0.3.linux.x86_64.gnu.opt.spx2.none
    -rwxr-xr-x 1 hoge hoge 11383240  2月  6 23:46 scip-8.0.3.linux.x86_64.gnu.opt.spx2.none
    -rwxr-xr-x 1 hoge hoge 11402416  2月  6 22:29 scip-8.0.3.linux.x86_64.gnu.opt.spx2.tny
    lrwxrwxrwx 1 hoge hoge       41  2月  5 06:01 scip.linux.x86_64.gnu.opt.spx2.none -> scip-8.0.3.linux.x86_64.gnu.opt.spx2.none
    lrwxrwxrwx 1 hoge hoge       40  2月  2 20:59 scip.linux.x86_64.gnu.opt.spx2.tny -> scip-8.0.3.linux.x86_64.gnu.opt.spx2.tny

    # example の make
    $ make
    $ ls -l bin/
    lrwxrwxrwx 1 hoge hoge       41  2月  6 23:47 brachistochrone -> brachistochrone.linux.x86_64.gnu.opt.spx2
    -rwxr-xr-x 1 hoge hoge 11379000  2月  7 00:05 brachistochrone.linux.x86_64.gnu.opt.spx2

    $ bin/brachistochrone
    ```

  - SCIPsolve(scip) で動作することを確認した
  - ldd で動的リンクされているライブラリを確認
    ```sh
    $ ldd bin/brachistochrone
        linux-vdso.so.1 (0x00007ffed81d8000)
        libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x00007f4c1b332000)
        libgmp.so.10 => /lib/x86_64-linux-gnu/libgmp.so.10 (0x00007f4c1b2ae000)
        libreadline.so.8 => /lib/x86_64-linux-gnu/libreadline.so.8 (0x00007f4c1b25e000)
        libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f4c1b10f000)
        libstdc++.so.6 => /lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007f4c1af2d000)
        libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007f4c1af12000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f4c1ad1e000)
        libtinfo.so.6 => /lib/x86_64-linux-gnu/libtinfo.so.6 (0x00007f4c1acee000)
        /lib64/ld-linux-x86-64.so.2 (0x00007f4c1c181000)
    ```
    SCIPまわりはなさそう
 
### .nl ファイルへの 変数情報の付与(スキル名や防具名など)
- symbolic_solver_labels オプションを有効化して nlファイルを出力し, そのnlファイルを scip solver に解かせれば 対話型シェルの ```display solution``` コマンドや C/C++ API の ```SCIP_CALL( SCIPprintSol(scip, SCIPgetBestSol(scip), NULL, FALSE) );``` などでスキル名等の情報込みの変数を見ることができる
  ```py
  mdl.write("dmax_sample_p.nl", io_options={'symbolic_solver_labels': True})
  ```

