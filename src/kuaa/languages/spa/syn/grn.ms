## intensificación, comparación (necesita concordancia grd:grd);
## en casos predicativos, estar o ser recibe el rasgo grd
## en casos atributivos, es el adjetivo
muy_adj :: muy [pos=a,grd=ete] ; // 0
mas_adj1 :: más [pos=a,grd=ve] ; // 0
mas_adj2 :: mas [pos=a,grd=ve] ; // 0
demasiado :: demasiado [pos=a,grd=eterei] ; // 0
#estar_muy :: estar_v[grd=ete] muy ; // 1
#ser_muy :: ser_v[grd=ete] muy ; // 1

### estar + adj sin sustantivo siguiente; introduce rasgo nuevo: ±perm
estar_adj :: estar_v [pos=a,-perm] ![pos=n] ; 0=>1 p,n,tm ; // 0 ; 1-> [pos=v]
ser_adj :: ser_v [pos=a,+perm] ![pos=n] ; 0=>1 p,n,tm ; // 0 ; 1-> [pos=v]

## reflexivo
refl/3 :: se [+fin,pos=v,p=3,voz=reflx,+r] ; // 0 
refl/1s :: me [+fin,pos=v,p=1,n=0,voz=reflx,+r] ; // 0
refl/2s :: te [+fin,pos=v,p=2,n=0,voz=reflx,+r] ; // 0
refl/1p :: nos [+fin,pos=v,p=1,n=1,voz=reflx,+r] ; // 0

## auxiliares, condicional
perf :: haber_v[tm=prs] [pos=v,tm=prc,asp=[+prf]] ; 0=>1 p,n ; // 0 ; 1-> [tm=prs,+fin]
pcp :: haber_v[tm=ipf] [pos=v,tm=prc] ; 0=>1 p,n ; // 0 ; 1-> [tm=pcp,+fin]
cnd_prf :: haber_v[tm=cnd] [pos=v,tm=prc] ; 0=>1 p,n ; // 0 ; 1-> [tm=cnd,+fin]
sbi_prf :: haber_v[tm=sbi] [pos=v,tm=prc] ; 0=>1 p,n ; // 0 ; 1-> [tm=prt,+fin]
sbi :: [pos=v,tm=sbi] ; 0 -> [tm=prt]
# this only works for present progressive
prog :: estar_v [pos=v,tm=ger,asp=[+prg]] ; 0=>1 p,n,tm ; // 0 ; 1-> [+fin]
pasivo :: ser_v [pos=v,tm=prc,voz=reflx,+r] ; 0=>1 p,n,tm ; // 0
# voy a ..., iba a ...; ignore tense of ir? ; prevent irse from triggering this
fut/ir :: ir_v[-r] a [pos=v,tm=inf] ; 0=>2 p,n ; // 0:2 1:2 ; 2-> [tm=fut,+fin]
# acabar de ...
acabar_de :: acabar_v[tm=prs] de [pos=v,tm=inf,asp=[+ramo]] ; 0=>2 p,n ; // 0:2 1:2 ; 2-> [tm=prs,+fin]
# comenzar/empezar a ...
comenzar_a :: comenzar_v a [pos=v,tm=inf] ; 0=>2 p,n ; // 1 ; 2-> [tm=prs,+fin]
empezar_a :: empezar_v a [pos=v,tm=inf] ; 0=>2 p,n ; // 1 ; 2-> [tm=prs,+fin]
# seguir + ger
seguir_ger :: seguir_v [pos=v,tm=ger] ; 0=>1 p,n,tm ; 1-> [+fin]

## derivación 1
volativo :: querer_v [pos=v,tm=inf,asp=[+vol]] ; 0=>1 p,n,tm,asp ; 1-> [+fin] ; // 0
obligacion_prs :: tener_v[tm=prs] que [pos=v,tm=inf] ; 0=>2 p,n ; 2-> [+fin,tm=fut,asp=[+obl]] ; // 0 1
obligacion_fut :: tener_v[tm=fut] que [pos=v,tm=inf] ; 0=>2 p,n ; 2-> [+fin,tm=fut,asp=[+obl]] ; // 0 1

## otros pronombres clíticos
obj/1s :: me [+fin,pos=v,po=1,no=0] ; // 0
obj/13s :: me lo [+fin,pos=v,po=1,no=0] ; // 0 1
obj/13s :: me los [+fin,pos=v,po=1,no=0] ; // 0 1
obj/2s :: te [+fin,pos=v,po=2,no=0] ; // 0
obj/23s :: te lo [+fin,pos=v,po=2,no=0] ; // 0 1
obj/13s :: te los [+fin,pos=v,po=2,no=0] ; // 0 1
obj/1p :: nos [+fin,pos=v,po=1,no=1] ; // 0
obj/12p :: nos lo [+fin,pos=v,po=1,no=1] ; // 0 1
obj/13s :: nos los [+fin,pos=v,po=1,no=1] ; // 0 1
# 2 o 3 persona
obj/3sd :: le [+fin,pos=v,po=3,no=0] ; // 0
obj/3sm :: lo [+fin,pos=v,po=3,no=0] ; // 0
obj/3sf :: la [+fin,pos=v,po=3,no=0] ; // 0
obj/3pm :: los [+fin,pos=v,po=3,no=1] ; // 0
obj/3pf :: las [+fin,pos=v,po=3,no=1] ; // 0
obj/3pd :: les [+fin,pos=v,po=3,no=1] ; // 0
obj/33d :: se le [+fin,pos=v,po=3,no=0] ; // 0 1
obj/33sm :: se lo [+fin,pos=v,po=3,no=0] ; // 0 1
obj/33sf :: se la [+fin,pos=v,po=3,no=0] ; // 0 1
obj/33pm :: se los [+fin,pos=v,po=3,no=1] ; // 0 1
obj/33pf :: se las [+fin,pos=v,po=3,no=1] ; // 0 1
obj/33pd :: se les [+fin,pos=v,po=3,no=1] ; // 0 1
#obj/3pm :: los [+fin,pos=v,po=3,no=1][+fin,pos=v,po=2,no=1] ; // 0
#obj/3pf :: las [+fin,pos=v,po=3,no=1][+fin,pos=v,po=2,no=1] ; // 0
#obj/3pd :: les [+fin,pos=v,po=3,no=1][+fin,pos=v,po=2,no=1] ; // 0

## ambigüedad de 2, 3 persona
# 3 pers sin ambigüedad
suj/3sm :: él [+fin,pos=v,p=3,n=0]
suj/3pm :: ellos [+fin,pos=v,p=3,n=1]
suj/3sf :: ella [+fin,pos=v,p=3,n=0]
suj/3pf :: ellas [+fin,pos=v,p=3,n=1]
suj/3sn :: [pos=n,n=0] [+fin,pos=v,p=3,n=0]
suj/3pn :: [pos=n,n=1] [+fin,pos=v,p=3,n=1]
# 2 pers form sin ambigüedad
2s_form :: usted [+fin,pos=v,p=3,n=0] ; 1-> [p=2]
2p_form :: ustedes [+fin,pos=v,p=3,n=1] ; 1-> [p=2]
# 2 pers form con ambigüedad, sólo si 3sm, 3pm, 3sf, 3pf no se han aplicado
#**2formal :: [pos=v,+fin,p=3] ; 0-> [p=2] ; FAILIF suj/3

## negativo
# imperativo (hay otros casos?)
neg_ipv :: ¡ no [pos=v,tm=sbp,+negipv] ; // 0 ; 2-> [tm=ipv,p=2] ; 1-> [+ipv]
# que_neg_sbp :: que no [pos=v,tm=sbp,+neg] ; // 1
neg :: no [pos=v,+neg] ; // 0 ; FAILIF neg_ipv

## derivación 2
# PODER + V[inf]: copy person, number, and TAM from PODER to V; make PODER 3s; make V +fin
pot :: poder_v [pos=v,tm=inf] ; 0=>1 p,n,po,no ; 1-> [+fin,tm=prs] ; 0-> [p=3]

## posesivo
pos/1s.s :: mi [pos=n,n=0,poses=[+ext,pp=1,np=0]] ; // 0
pos/1s.p :: mis [pos=n,n=1,poses=[+ext,pp=1,np=0]] ; // 0
pos/2s.s :: tu [pos=n,n=0,poses=[+ext,pp=2,np=0]] ; // 0
pos/2s.p :: tus [pos=n,n=1,poses=[+ext,pp=2,np=0]] ; // 0
# pueden ser también 2 persona
pos/3s.s :: su [pos=n,n=0,poses=[-ext,pp=3]] ; // 0
pos/3s.p :: sus [pos=n,n=1,poses=[-ext,pp=3]] ; // 0
#pos/3s.s :: su [pos=n,n=0,poses=[-ext,pp=3]][pos=n,n=0,poses=[+ext,pp=2]] ; // 0
#pos/3s.p :: sus [pos=n,n=1,poses=[-ext,pp=3]][pos=n,n=1,poses=[+ext,pp=2]] ; // 0
pos/1p.s :: nuestro [pos=n,n=0,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.p :: nuestros [pos=n,n=1,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.s :: nuestra [pos=n,n=0,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.p :: nuestras [pos=n,n=1,poses=[+ext,pp=1,np=1]] ; // 0

## algunas cláusulas relativas, nominales, y adverbiales
lo_que :: lo que [pos=v,rel=sjoj] ; // 0 1
al_inf :: a el [pos=v,tm=inf,pp=vove] ; // 0 1 ; 2-> [tm=prs,+fin]
# ambiguo, e.g., dije a mi vecino que vendrá
# *rel_sj :: [pos=n] que [pos=v,rel=sjoj] ; // 1

## artículos definitivos
artdef/ms :: el[pos=det] [pos=n] ; // 0
artdef/nom_m :: el[pos=det] %C ; // 0
artdef/nom_f :: la[pos=det] %C ; // 0
artdef/ms_adj :: el[pos=det] [pos=a,n=0] ; // 0
artdev/neut_adj :: lo[pos=det] [pos=a,n=0] ; // 0
artdef/fs :: la[pos=det] [pos=n] ; // 0
artdef/fs_adj :: la[pos=det] [pos=a,n=0] ; // 0
artdef/mp :: los[pos=det] [pos=n] ; // 0
artdef/mp_adj :: los[pos=det] [pos=a,n=1] ; // 0
artdef/mp_num :: los[pos=det] %N ; // 0
artdef/fp :: las[pos=det] [pos=n] ; // 0
artdef/fp_adj :: las[pos=det] [pos=a,n=1] ; // 0
artdef/fp_num :: las[pos=det] %N ; // 0

## preguntas
pregunta :: ¿ [pos=v,+inter] ; // 0

## infinitivos (deben ser finitos para coincidir con propiedades en grupos de verbos (v.grp))
infin :: [pos=v,tm=inf] ; 0-> [+fin]

## sujetos y complementos de la misma persona; hacer reflexivo (debe coincidir "estrictamente")
refl_1s :: *[+fin,n=0,no=0,p=1,po=1,pos=v,-r] ; 0 -> [+r,po=3]
refl_2s :: *[+fin,n=0,no=0,p=2,po=2,pos=v,-r] ; 0 -> [+r,po=3]
#refl_3 :: *[+fin,p=3,po=3,pos=v,-r] ; 0 -> [+r]
refl_1p :: *[+fin,n=1,no=1,p=1,po=1,pos=v,-r] ; 0 -> [+r,po=3]
refl_2p :: *[+fin,n=1,no=1,p=2,po=2,pos=v,-r] ; 0 -> [+r,po=3]

## imperativo negativo
impv_neg :: [+fin,n=0,pos=v,p=2,tm=sbp,+neg] ; 0 -> [tm=ipv,-neg,+negipv]
