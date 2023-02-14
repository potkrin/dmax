* SCIP STATISTICS
*   Problem name     : scipsample
*   Variables        : 3 (0 binary, 3 integer, 0 implicit integer, 0 continuous)
*   Constraints      : 2
NAME          scipsample
OBJSENSE
  MAX
ROWS
 N  Obj 
 E  const_constant 
 L  const_1 
COLUMNS
    INTSTART        'MARKER'                                  'INTORG'                                 
    x[AB]           Obj                                   15  const_1                                2 
    x[CB]           Obj                                   18  const_1                                2 
    x[WE]           Obj                                   30  const_constant                         1 
    x[WE]           const_1                                2 
    INTEND          'MARKER'                                  'INTEND'                                 
RHS
    RHS             const_constant                         0  const_1                               60 
BOUNDS
 PL Bound           x[AB]                                    
 PL Bound           x[CB]                                    
 PL Bound           x[WE]                                    
ENDATA