## auxiliares
perf :: haber_v [pos=v,tm=prc,asp=[+prf]] ; 0=>1 p,n,tm ; // 0
prog :: estar_v [pos=v,tm=ger,asp=[+prg]] ; 0=>1 p,n,tm ; // 0
pasivo :: ser_v [pos=v,tm=prc,voz=reflx] ; 0=>1 p,n,tm ; // 0
# voy a ..., iba a ...; ignore tense of ir?
fut/ir :: ir_v a [pos=v,tm=inf] ; 0=>2 p,n ; // 0 1 ; 2-> [tm=fut]

## derivación 1
volativo :: querer_v [pos=v,tm=inf,asp=[+vol]] ; 0=>1 p,n,tm,asp ; // 0

## reflexivo
refl/3 :: se [pos=v,p=3,voz=reflx,+r] ; // 0 
refl/1s :: me [pos=v,p=1,n=0,voz=reflx,+r] ; // 0
refl/2s :: te [pos=v,p=2,n=0,voz=reflx,+r] ; // 0
refl/1p :: nos [pos=v,p=1,n=1,voz=reflx,+r] ; // 0

### ser + adj with no noun following
#ser_adj :: ser_v [pos=a] ![pos=n] ; 0=>1 p,n,tm ; // 0 ; 1-> [pos=v]

## otros pronombres clíticos
obj/1s :: me [pos=v,po=1,no=0] ; // 0
obj/2s :: te [pos=v,po=2,no=0] ; // 0
obj/1p :: nos [pos=v,po=1,no=1] ; // 0
obj/3sm :: lo [pos=v,po=3,no=0] ; >< 0 1
obj/3sf :: la [pos=v,po=3,no=0] ; >< 0 1
obj/3sd :: le [pos=v,po=3,no=0] ; // 0 ; ++ 2 a, 3 él
obj/3pm :: los [pos=v,po=3,no=1] ; >< 0 1
obj/3pf :: las [pos=v,po=3,no=1] ; >< 0 1
obj/3pd :: les [pos=v,po=3,no=1] ; >< 0 1

## ambigüedad de 2, 3 persona
# 3 pers sin ambigüedad
suj/3sm :: él [pos=v,p=3,n=0]
suj/3pm :: ellos [pos=v,p=3,n=1]
suj/3sf :: ella [pos=v,p=3,n=0]
suj/3pf :: ellas [pos=v,p=3,n=1]
# 2 pers form sin ambigüedad
2s_form :: usted [pos=v,p=3,n=0] ; 1-> [p=2]
# 2 pers form con ambigüedad, sólo si 3sm, 3pm, 3sf, 3pf no se aplicaron
**2formal :: [pos=v,+fin,p=3] ; 0-> [p=2] ; FAILIF suj/3

## negativo
# imperativo (debe aplicarse antes de la regla más general)
neg_ipv :: no [pos=v,tm=sbp,+negipv] ; 1-> [tm=ipv] ; 0-> [+ipv]
neg :: no [pos=v,+neg] ; // 0 ; FAILIF neg_

## derivación 2
pot :: poder_v [pos=v,tm=inf] ; 0=>1 p,n,tm

## posesivo
pos/1s.s :: mi [pos=n,n=0,poses=[+ext,pp=1,np=0]] ; // 0
pos/1s.p :: mis [pos=n,n=1,poses=[+ext,pp=1,np=0]] ; // 0
pos/2s.s :: tu [pos=n,n=0,poses=[+ext,pp=2,np=0]] ; // 0
pos/2s.p :: tus [pos=n,n=1,poses=[+ext,pp=2,np=0]] ; // 0
pos/3s.s :: su [pos=n,n=0,poses=[-ext,pp=3]] ; // 0
pos/3s.p :: sus [pos=n,n=1,poses=[-ext,pp=3]] ; // 0
pos/1p.s :: nuestro [pos=n,n=0,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.p :: nuestros [pos=n,n=1,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.s :: nuestra [pos=n,n=0,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.p :: nuestras [pos=n,n=1,poses=[+ext,pp=1,np=1]] ; // 0

## artículos definitivos
artdef/ms :: el [pos=n,n=0] ; // 0
artdef/fs :: la [pos=n,n=0] ; // 0
artdef/mp :: los [pos=n,n=1] ; // 0
artdef/fp :: las [pos=n,n=1] ; // 0
artdef/ms_adj :: el [pos=a,n=0] [pos=n,n=0] ; // 0
artdef/fs_adj :: la [pos=a,n=0] [pos=n,n=0] ; // 0
artdef/mp_adj :: los [pos=a,n=1] [pos=n,n=1] ; // 0
artdef/fp_adj :: las [pos=a,n=1] [pos=n,n=1] ; // 0

## intensificación (necesita concordancia grd:grd);
## en casos predicativos, estar o ser recibe el rasgo grd
## en casos atributivos, es el adjetivo
estar_muy :: estar_v[grd=ete] muy ; // 1
ser_muy :: ser_v[grd=ete] muy ; // 1
muy_adj :: muy [pos=a,grd=ete] ; // 0

## cláusulas relativas
*rel_sj :: [pos=n] que [pos=v,rel=sjoj] ; // 1

## cláusulas adverbiales
donde :: donde [pos=v,rel=obl] ; // 0

### preposiciones
#a/pp :: a [pos=n,caso=pe] ; // 0
#en/pp :: en [pos=n,caso=pe] ; // 0
