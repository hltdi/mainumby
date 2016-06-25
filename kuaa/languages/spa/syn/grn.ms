### estar + adj sin sustantivo siguiente; introduce rasgo nuevo: ±perm
estar_adj :: estar_v [pos=a,-perm] ![pos=n] ; 0=>1 p,n,tm ; // 0 ; 1-> [pos=v]
ser_adj :: ser_v [pos=a,+perm] ![pos=n] ; 0=>1 p,n,tm ; // 0 ; 1-> [pos=v]

## auxiliares
perf :: haber_v[tm=prs] [pos=v,tm=prc,asp=[+prf]] ; 0=>1 p,n ; // 0 ; 1-> [tm=prs]
pcp :: haber_v[tm=ipf] [pos=v,tm=prc] ; 0=>1 p,n ; // 0 ; 1-> [tm=pcp]
prog :: estar_v [pos=v,tm=ger,asp=[+prg]] ; 0=>1 p,n,tm ; // 0
pasivo :: ser_v [pos=v,tm=prc,voz=reflx,+r] ; 0=>1 p,n,tm ; // 0
# voy a ..., iba a ...; ignore tense of ir?
fut/ir :: ir_v a [pos=v,tm=inf] ; 0=>2 p,n ; // 0:2 1:2 ; 2-> [tm=fut]
# acabar de ...
acabar_de :: acabar_v[tm=prs] de [pos=v,tm=inf,asp=[+ramo]] ; 0=>2 p,n ; // 0:2 1:2 ; 2-> [tm=prs]
# comenzar/empezar a ...
comenzar_a :: comenzar_v a [pos=v,tm=inf] ; 0=>2 p,n ; // 1 ; 2-> [tm=prs]
empezar_a :: empezar_v a [pos=v,tm=inf] ; 0=>2 p,n ; // 1 ; 2-> [tm=prs]
# seguir + ger
seguir_ger :: seguir_v [pos=v,tm=ger] ; 0=>1 p,n,tm

## derivación 1
volativo :: querer_v [pos=v,tm=inf,asp=[+vol]] ; 0=>1 p,n,tm,asp ; // 0

## artículos definitivos
# antes adjetivos sin substantivo
artdef/adj_fs :: la [pos=a,n=0,rel=sjoj] ![pos=n] ; // 0
artdef/adj_ms :: el [pos=a,n=0,rel=sjoj] ![pos=n] ; // 0
artdef/adj_fp :: las [pos=a,n=1,rel=sjoj] ![pos=n] ; // 0
artdef/adj_mp :: los [pos=a,n=1,rel=sjoj] ![pos=n] ; // 0 ; 1-> [pos=v]
# con adjetivo o número entre el artículo y el sustantivo
artdef/ms_adj :: el [pos=a,n=0] [pos=n,n=0] ; // 0:2
# ambiguo??
#*=artdef/fs_adj :: la [pos=a,n=0] [pos=n,n=0] ; // 0:2
#*=artdef/mp_adj :: los [pos=a,n=1] [pos=n,n=1] ; // 0:2
#*=artdef/fp_adj :: las [pos=a,n=1] [pos=n,n=1] ; // 0:2
artdef/fs_adj :: la [pos=a,n=0] [pos=n,n=0] ; // 0:2
artdef/mp_adj :: los [pos=a,n=1] [pos=n,n=1] ; // 0:2
artdef/fp_adj :: las [pos=a,n=1] [pos=n,n=1] ; // 0:2
artdef/ms :: el [pos=n,n=0] ; // 0
#*=artdef/fs :: la [pos=n,n=0] ; // 0
#*=artdef/mp :: los [pos=n,n=1] ; // 0
#*=artdef/fp :: las [pos=n,n=1] ; // 0
artdef/fs :: la [pos=n,n=0] ; // 0
artdef/mp :: los [pos=n,n=1] ; // 0
artdef/fp :: las [pos=n,n=1] ; // 0
# con dos adjetivos antes del sustantivo
#...

## reflexivo
refl/3 :: se [pos=v,p=3,voz=reflx,+r] ; // 0 
refl/1s :: me [pos=v,p=1,n=0,voz=reflx,+r] ; // 0
refl/2s :: te [pos=v,p=2,n=0,voz=reflx,+r] ; // 0
refl/1p :: nos [pos=v,p=1,n=1,voz=reflx,+r] ; // 0

## otros pronombres clíticos
obj/1s :: me [pos=v,po=1,no=0] ; // 0
obj/2s :: te [pos=v,po=2,no=0] ; // 0
obj/1p :: nos [pos=v,po=1,no=1] ; // 0
obj/3sd :: le [pos=v,po=3,no=0] ; // 0
obj/3sm :: lo [pos=v,po=3,no=0] ; // 0
obj/3sf :: la [pos=v,po=3,no=0] ; // 0
obj/3pm :: los [pos=v,po=3,no=1] ; // 0
obj/3pf :: las [pos=v,po=3,no=1] ; // 0
obj/3pd :: les [pos=v,po=3,no=1] ; // 0
# old versions that preserved and postposed the pronoun
# obj/3sf :: la [pos=v,po=3,no=0] ; >< 0 1
# obj/3sd :: le [pos=v,po=3,no=0] ; // 0 ; ++ 2 a, 3 él

## ambigüedad de 2, 3 persona
# 3 pers sin ambigüedad
suj/3sm :: él [pos=v,p=3,n=0]
suj/3pm :: ellos [pos=v,p=3,n=1]
suj/3sf :: ella [pos=v,p=3,n=0]
suj/3pf :: ellas [pos=v,p=3,n=1]
# 2 pers form sin ambigüedad
2s_form :: usted [pos=v,p=3,n=0] ; 1-> [p=2]
2p_form :: ustedes [pos=v,p=3,n=1] ; 1-> [p=2]
# 2 pers form con ambigüedad, sólo si 3sm, 3pm, 3sf, 3pf no se han aplicado
#**2formal :: [pos=v,+fin,p=3] ; 0-> [p=2] ; FAILIF suj/3

## negativo
# imperativo (hay otros casos?)
neg_ipv :: ¡ no [pos=v,tm=sbp,+negipv] ; // 0 ; 2-> [tm=ipv,p=2] ; 1-> [+ipv]
# que_neg_sbp :: que no [pos=v,tm=sbp,+neg] ; // 1
# # imperativo (debe aplicarse antes de la regla más general)
# neg_ipv :: no [pos=v,tm=sbp,+negipv] ; 1-> [tm=ipv] ; 0-> [+ipv] ; FAILIF que_neg_
neg :: no [pos=v,+neg] ; // 0 ; FAILIF neg_ipv

## derivación 2
pot :: poder_v [pos=v,tm=inf] ; 0=>1 p,n,tm

## posesivo
pos/1s.s :: mi [pos=n,n=0,poses=[+ext,pp=1,np=0]] ; // 0
pos/1s.p :: mis [pos=n,n=1,poses=[+ext,pp=1,np=0]] ; // 0
pos/2s.s :: tu [pos=n,n=0,poses=[+ext,pp=2,np=0]] ; // 0
pos/2s.p :: tus [pos=n,n=1,poses=[+ext,pp=2,np=0]] ; // 0
# pueden ser también 2 persona
pos/3s.s :: su [pos=n,n=0,poses=[-ext,pp=3]] ; // 0
pos/3s.p :: sus [pos=n,n=1,poses=[-ext,pp=3]] ; // 0
pos/1p.s :: nuestro [pos=n,n=0,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.p :: nuestros [pos=n,n=1,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.s :: nuestra [pos=n,n=0,poses=[+ext,pp=1,np=1]] ; // 0
pos/1p.p :: nuestras [pos=n,n=1,poses=[+ext,pp=1,np=1]] ; // 0

## intensificación, comparación (necesita concordancia grd:grd);
## en casos predicativos, estar o ser recibe el rasgo grd
## en casos atributivos, es el adjetivo
estar_muy :: estar_v[grd=ete] muy ; // 1
ser_muy :: ser_v[grd=ete] muy ; // 1
muy_adj :: muy [pos=a,grd=ete] ; // 0
mas_adj1 :: más [pos=a,grd=ve] ; // 0
mas_adj2 :: mas [pos=a,grd=ve] ; // 0
demasiado :: demasiado [pos=a,grd=eterei] ; // 0

## cláusulas relativas y nominales
# ambiguo, e.g., dije a mi vecino que vendrá
*rel_sj :: [pos=n] que [pos=v,rel=sjoj] ; // 1
lo_que :: lo que [pos=v,rel=sjoj] ; // 0 1
# cómo representar relativo objetivo con sujeto antes del verbo
# el carro que mi vecino compró

## cláusulas adverbiales
al_inf :: a el [pos=v,tm=inf,pp=vove] ; // 0 1 ; 2-> [tm=prs]
a_donde_rel :: a donde [pos=v,rel=obl,pp=pe] ; // 0 1
donde_rel :: [pos=n] donde [pos=v,rel=obl] ; // 1
al_que_rel :: [pos=n] a el que [pos=v,rel=obl] ; // 0 1 2
a_la_que_rel :: [pos=n] a la que [pos=v,rel=obl] ; // 0 1 2
a_los_que_rel :: [pos=n] a los que [pos=v,rel=obl] ; // 0 1 2
a_las_que_rel :: [pos=n] a las que [pos=v,rel=obl] ; // 0 1 2
# otras preposiciones: en, con?, por?...
#...

## preguntas
pregunta :: ¿ [pos=v,+inter] ; // 0
