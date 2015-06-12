## auxiliares
perfecto :: haber_ [pos=v,tm=prc,+prf] ; 0=>1 p,n,tm ; // 0
progresivo :: estar_ [pos=v,tm=ger,+prg] ; 0=>1 p,n,tm ; // 0
pasivo :: ser_ [pos=v,tm=prc,+psv] ; 0=>1 p,n,tm ; // 0
# voy a ..., iba ...
futuro/ir :: ir_ a [pos=v,tm=inf,+fut] ; 0=>2 p,n,tm ; // 0 1

## derivación
volativo :: querer_ [pos=v,tm=inf,+vol] ; 0=>1 p,n,tm ; // 0

## reflexivo
reflexivo/3 :: se [pos=v,p=3,+rflx] ; // 0 
reflexivo/1s :: me [pos=v,p=3,n=0,+rflx] ; // 0
reflexivo/2s :: te [pos=v,p=2,n=0,+rflx] ; // 0
reflexivo/1p :: nos [pos=v,p=1,n=1,+rflx] ; // 0

## negativo
negativo :: no [pos=v,+neg] ; // 0
