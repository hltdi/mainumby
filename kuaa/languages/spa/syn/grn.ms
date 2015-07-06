## auxiliares
perfecto :: haber_v [pos=v,tm=prc,asp=[+prf]] ; 0=>1 p,n,tm ; // 0
progresivo :: estar_v [pos=v,tm=ger,asp=[+prg]] ; 0=>1 p,n,tm ; // 0
pasivo :: ser_v [pos=v,tm=prc,voz=reflx] ; 0=>1 p,n,tm ; // 0
# voy a ..., iba a ...; ignore tense of ir?
futuro/ir :: ir_v a [pos=v,tm=inf] ; 0=>2 p,n ; // 0 1 ; 2-> [tm=fut]

## derivación
volativo :: querer_v [pos=v,tm=inf,misc=[+vol]] ; 0=>1 p,n,tm ; // 0

## reflexivo
reflexivo/3 :: se [pos=v,p=3,voz=reflx,+r] ; // 0 
reflexivo/1s :: me [pos=v,p=3,n=0,voz=reflx,+r] ; // 0
reflexivo/2s :: te [pos=v,p=2,n=0,voz=reflx,+r] ; // 0
reflexivo/1p :: nos [pos=v,p=1,n=1,voz=reflx,+r] ; // 0

## negativo
negativo :: no [pos=v,+neg] ; // 0
