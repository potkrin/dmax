* SCIP STATISTICS
*   Problem name     : t_scipsample
*   Variables        : 0 (0 binary, 0 integer, 0 implicit integer, 0 continuous)
*   Constraints      : 0
NAME          t_scipsample
OBJSENSE
  MAX
ROWS
 N  Obj 
COLUMNS
    INTSTART  'MARKER'                            'INTORG'                           
    t_x[CB]   Obj                              0 
    t_x[WE]   Obj                              0 
    INTEND    'MARKER'                            'INTEND'                           
RHS
    RHS       Obj                           -540 
BOUNDS
 FX Bound     t_x[CB]                         30 
 FX Bound     t_x[WE]                          0 
ENDATA