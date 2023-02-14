g3 1 1 0	# problem Sample
 3 2 1 0 1 	# vars, constraints, objectives, ranges, eqns
 0 0 0 0 0 0	# nonlinear constrs, objs; ccons: lin, nonlin, nd, nzlb
 0 0	# network constraints: nonlinear, linear
 0 0 0 	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 3 0 0 0 	# discrete variables: binary, integer, nonlinear (b,c,o)
 4 3 	# nonzeros in Jacobian, obj. gradient
 14 5	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
C0	#const_constant
n0
C1	#const_1
n0
O0 1	#value
n0
x0	# initial guess
r	#2 ranges (rhs's)
4 0.0
1 60.0
b	#3 bounds (on variables)
2 0
2 0
2 0
k2	#intermediate Jacobian column lengths
1
2
J0 1
2 1
J1 3
0 2
1 2
2 2
G0 3
0 15
1 18
2 30
