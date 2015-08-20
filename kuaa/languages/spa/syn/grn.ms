## auxiliares
perfecto :: haber_v [pos=v,tm=prc,asp=[+prf]] ; 0=>1 p,n,tm ; // 0
progresivo :: estar_v [pos=v,tm=ger,asp=[+prg]] ; 0=>1 p,n,tm ; // 0
pasivo :: ser_v [pos=v,tm=prc,voz=reflx] ; 0=>1 p,n,tm ; // 0
# voy a ..., iba a ...; ignore tense of ir?
futuro/ir :: ir_v a [pos=v,tm=inf] ; 0=>2 p,n ; // 0 1 ; 2-> [tm=fut]

## derivación 1
volativo :: querer_v [pos=v,tm=inf,asp=[+vol]] ; 0=>1 p,n,tm,asp ; // 0

## reflexivo
reflexivo/3 :: se [pos=v,p=3,voz=reflx,+r] ; // 0 
reflexivo/1s :: me [pos=v,p=1,n=0,voz=reflx,+r] ; // 0
reflexivo/2s :: te [pos=v,p=2,n=0,voz=reflx,+r] ; // 0
reflexivo/1p :: nos [pos=v,p=1,n=1,voz=reflx,+r] ; // 0

### ser + adj with no noun following
#ser_adj :: ser_v [pos=a] ![pos=n] ; 0=>1 p,n,tm ; // 0 ; 1-> [pos=v]

## otros pronombres clíticos
objeto/1s :: me [pos=v,po=1,no=0] ; // 0
objeto/2s :: te [pos=v,po=2,no=0] ; // 0
objeto/1p :: nos [pos=v,po=1,no=1] ; // 0
objeto/3sm :: lo [pos=v,po=3,no=0] ; // 0
objeto/3sf :: la [pos=v,po=3,no=0] ; // 0
objeto/3sd :: le [pos=v,po=3,no=0] ; // 0
objeto/3pm :: los [pos=v,po=3,no=1] ; // 0
objeto/3pf :: las [pos=v,po=3,no=1] ; // 0
objeto/3pd :: les [pos=v,po=3,no=1] ; // 0

## negativo
negativo :: no [pos=v,+neg] ; // 0

## derivación 2
potencial :: poder_v [pos=v,tm=inf] ; 0=>1 p,n,tm

## posesivo
posesivo/1s.s :: mi [pos=n,n=0,poses=[+ext,pp=1,np=0]] ; // 0
posesivo/1s.p :: mis [pos=n,n=1,poses=[+ext,pp=1,np=0]] ; // 0
posesivo/2s.s :: tu [pos=n,n=0,poses=[+ext,pp=2,np=0]] ; // 0
posesivo/2s.p :: mus [pos=n,n=1,poses=[+ext,pp=2,np=0]] ; // 0
posesivo/3s.s :: su [pos=n,n=0,poses=[+ext,pp=3]] ; // 0
posesivo/3s.p :: sus [pos=n,n=1,poses=[+ext,pp=3]] ; // 0
posesivo/1p.s :: nuestro [pos=n,n=0,poses=[+ext,pp=1,np=1]] ; // 0
posesivo/1p.p :: nuestros [pos=n,n=1,poses=[+ext,pp=1,np=1]] ; // 0
posesivo/1p.s :: nuestra [pos=n,n=0,poses=[+ext,pp=1,np=1]] ; // 0
posesivo/1p.p :: nuestras [pos=n,n=1,poses=[+ext,pp=1,np=1]] ; // 0

## artículos definitivos
artdef/ms :: el [pos=n,n=0] ; // 0
artdef/fs :: la [pos=n,n=0] ; // 0
artdef/mp :: los [pos=n,n=1] ; // 0
artdef/fp :: las [pos=n,n=1] ; // 0
artdef/ms_adj :: el [pos=a,n=0] [pos=n,n=0] ; // 0
artdef/fs_adj :: la [pos=a,n=0] [pos=n,n=0] ; // 0
artdef/mp_adj :: los [pos=a,n=1] [pos=n,n=1] ; // 0
artdef/fp_adj :: las [pos=a,n=1] [pos=n,n=1] ; // 0

## intensificación (necesita concordancia grd:grd)
muy :: muy [pos=a,grd=ete] ; // 0

### preposiciones
#a/pp :: a [pos=n,caso=pe] ; // 0
#en/pp :: en [pos=n,caso=pe] ; // 0


