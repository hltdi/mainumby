### PATTERNS
## vos imp: groups for accenting final syllable before mult suff
##     or not accenting syllable before single suffix
pat: vos_grp ([aeiou][^aeiouáéíóú]*?)([aei])$
pat: vos [aeiou]\w*?[áéí]$
# dame, dime, etc.
pat: vos1 ^d[ai]$
pat: vos1_grp ^([ds])([áíé])$
## tú, usted imp: groups for deaccenting penultimate syllable
pat: penult_acc_grp ([áéíóú])(\w*?[ae])$
# irregular tú imperatives: irr1: dé, sé; irr2: others
pat: irr1_grp ^([ds])e$
pat: irr1 ^[ds]é$
pat: irr2 ^\w[aeiou][ln]??$
pat: irr2_grp ^(\w)([áéíóú])([ln]??)$
## ustedes: groups for deaccenting penultimate syllable
pat: ustedes_grp ([áéíóú])(\w*?[ae]n)$
## nosotros: groups for deaccenting penultimate syllable; s added before nos/se
pat: nosotros_grp_s ([áéíóú])(\w*?mo)$
pat: nosotros_grp ([áéíóú])(\w*?mos)$
# infinitive
pat: inf r$
pat: inf_grp ([^e])([áéí])(r)$
pat: eir eír$
# gerund: deaccent penultimate syllable
pat: ger_grp ([áé])(ndo)$

### FEATURE STRUCTURES
## real imperative
gram: vos_ipv [p=2,n=0,tm=ipv]
# reflexive
gram: vos_ipv_refl [p=2,n=0,tm=ipv,+r]
# first person pronouns
gram: vos_ipv_1s [p=2,n=0,tm=ipv,-r,po=1,no=0]
gram: vos_ipv_1p [p=2,n=0,tm=ipv,-r,po=1,no=1]
gram: vos_ipv_1s_refl [p=2,n=0,tm=ipv,po=1,no=0,+r]
gram: vos_ipv_1p_refl [p=2,n=0,tm=ipv,po=1,no=1,+r]
# third person pronouns
gram: vos_ipv_3s [p=2,n=0,tm=ipv,-r,po=3,no=0]
gram: vos_ipv_3p [p=2,n=0,tm=ipv,-r,po=3,no=1]
gram: vos_ipv_3s_refl [p=2,n=0,tm=ipv,po=3,no=0,+r]
gram: vos_ipv_3p_refl [p=2,n=0,tm=ipv,po=3,no=1,+r]
# first and third person pronouns
gram: vos_ipv_1s3s [p=2,n=0,tm=ipv,-r,po=3,no=0,pi=1,ni=0]
gram: vos_ipv_1p3s [p=2,n=0,tm=ipv,-r,po=3,no=0,pi=1,ni=1]
gram: vos_ipv_1s3p [p=2,n=0,tm=ipv,-r,po=3,no=1,pi=1,ni=0]
gram: vos_ipv_1p3p [p=2,n=0,tm=ipv,-r,po=3,no=1,pi=1,ni=1]
# 2 third person pronouns
gram: vos_ipv_33s [p=2,n=0,tm=ipv,-r,po=3,no=0,pi=3]
gram: vos_ipv_33p [p=2,n=0,tm=ipv,-r,po=3,no=1,pi=3]
## imperative/subjunctive: usted
gram: usted_ipv [p=3,n=0,tm=sbp,+ipv]
# reflexive
gram: usted_ipv_refl [p=3,n=0,tm=sbp,+ipv,+r]
# first person pronouns
gram: usted_ipv_1s [p=3,n=0,tm=sbp,+ipv,-r,po=1,no=0]
gram: usted_ipv_1p [p=3,n=0,tm=sbp,+ipv,-r,po=1,no=1]
gram: usted_ipv_1s_refl [p=3,n=0,tm=sbp,+ipv,+r,po=1,no=0]
gram: usted_ipv_1p_refl [p=3,n=0,tm=sbp,+ipv,+r,po=1,no=1]
# third person pronouns
gram: usted_ipv_3s [p=3,n=0,tm=sbp,+ipv,-r,po=3,no=0]
gram: usted_ipv_3p [p=3,n=0,tm=sbp,+ipv,-r,po=3,no=1]
# ambiguous se + lo/la/las/los/le/les; indirect object or reflexive
gram: usted_ipv_33s [p=3,n=0,tm=sbp,+ipv,po=3,no=0,pi=3,-r]
gram: usted_ipv_33p [p=3,n=0,tm=sbp,+ipv,po=3,no=1,pi=3,-r]
gram: usted_ipv_3s_refl [p=3,n=0,tm=sbp,+ipv,po=3,no=0,+r]
gram: usted_ipv_3p_refl [p=3,n=0,tm=sbp,+ipv,po=3,no=1,+r]
# first and third persons: me+lo, etc.
gram: usted_ipv_1s3s [p=3,n=0,tm=sbp,+ipv,-r,pi=1,ni=0,po=3,no=0]
gram: usted_ipv_1s3p [p=3,n=0,tm=sbp,+ipv,-r,pi=1,ni=0,po=3,no=1]
gram: usted_ipv_1p3s [p=3,n=0,tm=sbp,+ipv,-r,pi=1,ni=1,po=3,no=0]
gram: usted_ipv_1p3p [p=3,n=0,tm=sbp,+ipv,-r,pi=1,ni=1,po=3,no=1]
# se+me+lo, etc.
gram: usted_ipv_1s3s_refl [p=3,n=0,tm=sbp,+ipv,+r,pi=1,ni=0,po=3,no=0]
gram: usted_ipv_1s3p_refl [p=3,n=0,tm=sbp,+ipv,+r,pi=1,ni=0,po=3,no=1]
gram: usted_ipv_1p3s_refl [p=3,n=0,tm=sbp,+ipv,+r,pi=1,ni=1,po=3,no=0]
gram: usted_ipv_1p3p_refl [p=3,n=0,tm=sbp,+ipv,+r,pi=1,ni=1,po=3,no=1]
## imperative/subjunctive: ustedes
gram: ustedes_ipv [p=3,n=1,tm=sbp,+ipv]
# reflexive
gram: ustedes_ipv_refl [p=3,n=1,tm=sbp,+ipv,+r]
# first person pronouns
gram: ustedes_ipv_1s [p=3,n=1,tm=sbp,+ipv,-r,po=1,no=0]
gram: ustedes_ipv_1p [p=3,n=1,tm=sbp,+ipv,-r,po=1,no=1]
gram: ustedes_ipv_1s_refl [p=3,n=1,tm=sbp,+ipv,+r,po=1,no=0]
gram: ustedes_ipv_1p_refl [p=3,n=1,tm=sbp,+ipv,+r,po=1,no=1]
# third person pronouns
gram: ustedes_ipv_3s [p=3,n=1,tm=sbp,+ipv,-r,po=3,no=0]
gram: ustedes_ipv_3p [p=3,n=1,tm=sbp,+ipv,-r,po=3,no=1]
# ambiguous se + lo/la/las/los/le/les; indirect object or reflexive
gram: ustedes_ipv_33s [p=3,n=1,tm=sbp,+ipv,po=3,no=0,pi=3,-r]
gram: ustedes_ipv_33p [p=3,n=1,tm=sbp,+ipv,po=3,no=1,pi=3,-r]
gram: ustedes_ipv_3s_refl [p=3,n=1,tm=sbp,+ipv,po=3,no=0,+r]
gram: ustedes_ipv_3p_refl [p=3,n=1,tm=sbp,+ipv,po=3,no=1,+r]
# first and third persons: me+lo, etc.
gram: ustedes_ipv_1s3s [p=3,n=1,tm=sbp,+ipv,-r,pi=1,ni=0,po=3,no=0]
gram: ustedes_ipv_1s3p [p=3,n=1,tm=sbp,+ipv,-r,pi=1,ni=0,po=3,no=1]
gram: ustedes_ipv_1p3s [p=3,n=1,tm=sbp,+ipv,-r,pi=1,ni=1,po=3,no=0]
gram: ustedes_ipv_1p3p [p=3,n=1,tm=sbp,+ipv,-r,pi=1,ni=1,po=3,no=1]
# se+me+lo, etc.
gram: ustedes_ipv_1s3s_refl [p=3,n=1,tm=sbp,+ipv,+r,pi=1,ni=0,po=3,no=0]
gram: ustedes_ipv_1s3p_refl [p=3,n=1,tm=sbp,+ipv,+r,pi=1,ni=0,po=3,no=1]
gram: ustedes_ipv_1p3s_refl [p=3,n=1,tm=sbp,+ipv,+r,pi=1,ni=1,po=3,no=0]
gram: ustedes_ipv_1p3p_refl [p=3,n=1,tm=sbp,+ipv,+r,pi=1,ni=1,po=3,no=1]
## imperative/subjunctive: nosotros
gram: nosotros_ipv [p=1,n=1,tm=sbp,+ipv]
# reflexive
gram: nosotros_ipv_refl [p=1,n=1,tm=sbp,+r,+ipv]
# third person pronouns
gram: nosotros_ipv_3s [p=1,n=1,tm=sbp,-r,po=3,no=0,+ipv]
gram: nosotros_ipv_3p [p=1,n=1,tm=sbp,-r,po=3,no=1,+ipv]
gram: nosotros_ipv_3s_refl [p=1,n=1,tm=sbp,+r,po=3,no=0,+ipv]
gram: nosotros_ipv_3p_refl [p=1,n=1,tm=sbp,+r,po=3,no=1,+ipv]
# second person pronouns
gram: nosotros_ipv_2s [p=1,n=1,tm=sbp,-r,po=2,no=0,+ipv]
gram: nosotros_ipv_2s_refl [p=1,n=1,tm=sbp,+r,po=2,no=0,+ipv]
# second and third person pronouns
gram: nosotros_ipv_2s3s [p=1,n=1,tm=sbp,-r,pi=2,ni=0,po=3,no=0,+ipv]
gram: nosotros_ipv_2s3p [p=1,n=1,tm=sbp,-r,pi=2,ni=0,po=3,no=1,+ipv]
# 2 third person pronouns
gram: nosotros_ipv_33s [p=1,n=1,tm=sbp,po=3,no=0,pi=3,-r,+ipv]
gram: nosotros_ipv_33p [p=1,n=1,tm=sbp,po=3,no=1,pi=3,-r,+ipv]
# infinitive; lots of ambiguity not handled
gram: inf [tm=inf]
gram: inf_3s [tm=inf,po=3,no=0,-r]
gram: inf_3p [tm=inf,po=3,no=1,-r]
gram: inf_1s [tm=inf,po=1,no=0,-r]
gram: inf_1p [tm=inf,po=1,no=1,-r]
gram: inf_2s [tm=inf,po=2,no=0,-r]
gram: inf_refl [tm=inf,+r,p=3]
gram: inf_1s2s [tm=inf,po=2,no=0,pi=1,ni=0,-r]
gram: inf_1p2s [tm=inf,po=2,no=0,pi=1,ni=1,-r]
gram: inf_2s_refl [tm=inf,po=2,no=0,+r]
# se+me, etc.
gram: inf_1s_refl [tm=inf,po=1,no=0,+r]
gram: inf_1p_refl [tm=inf,po=1,no=1,+r]
# me+lo, se+me+lo, etc.
gram: inf_1s3s [tm=inf,po=3,no=0,pi=1,ni=0,-r]
gram: inf_1s3s_refl [tm=inf,po=3,no=0,pi=1,ni=0,+r]
gram: inf_1s3p [tm=inf,po=3,no=1,pi=1,ni=0,-r]
gram: inf_1s3p_refl [tm=inf,po=3,no=1,pi=1,ni=0,+r]
gram: inf_1p3s [tm=inf,po=3,no=0,pi=1,ni=1,-r]
gram: inf_1p3s_refl [tm=inf,po=3,no=0,pi=1,ni=1,+r]
gram: inf_1p3p [tm=inf,po=3,no=1,pi=1,ni=1,-r]
gram: inf_1p3p_refl [tm=inf,po=3,no=1,pi=1,ni=1,+r]
gram: inf_2s3s [tm=inf,po=3,no=0,pi=2,ni=0,-r]
gram: inf_2s3s_refl [tm=inf,po=3,no=0,pi=2,ni=0,+r]
gram: inf_2s3p [tm=inf,po=3,no=1,pi=2,ni=0,-r]
gram: inf_2s3p_refl [tm=inf,po=3,no=1,pi=2,ni=0,+r]
gram: inf_33s [tm=inf,po=3,no=0,pi=3,-r]
gram: inf_33p [tm=inf,po=3,no=1,pi=3,-r]
# gerund; lots of ambiguity not handled
gram: ger [tm=ger]
gram: ger_3s [tm=ger,po=3,no=0,-r]
gram: ger_3p [tm=ger,po=3,no=1,-r]
gram: ger_1s [tm=ger,po=1,no=0,-r]
gram: ger_1p [tm=ger,po=1,no=1,-r]
gram: ger_2s [tm=ger,po=2,no=0,-r]
gram: ger_refl [tm=ger,+r,p=3]
gram: ger_1s2s [tm=ger,po=2,no=0,pi=1,ni=0,-r]
gram: ger_1p2s [tm=ger,po=2,no=0,pi=1,ni=1,-r]
gram: ger_1s_refl [tm=ger,po=1,no=0,+r]
gram: ger_1p_refl [tm=ger,po=1,no=1,+r]
gram: ger_2s_refl [tm=ger,po=2,no=0,+r]
gram: ger_1s3s [tm=ger,po=3,no=0,pi=1,ni=0,-r]
gram: ger_1s3p [tm=ger,po=3,no=1,pi=1,ni=0,-r]
gram: ger_1p3s [tm=ger,po=3,no=0,pi=1,ni=1,-r]
gram: ger_1p3p [tm=ger,po=3,no=1,pi=1,ni=1,-r]
gram: ger_2s3s [tm=ger,po=3,no=0,pi=2,ni=0,-r]
gram: ger_2s3p [tm=ger,po=3,no=1,pi=2,ni=0,-r]
gram: ger_1s3s_refl [tm=ger,po=3,no=0,pi=1,ni=0,+r]
gram: ger_1s3p_refl [tm=ger,po=3,no=1,pi=1,ni=0,+r]
gram: ger_1p3s_refl [tm=ger,po=3,no=0,pi=1,ni=1,+r]
gram: ger_1p3p_refl [tm=ger,po=3,no=1,pi=1,ni=1,+r]
gram: ger_2s3s_refl [tm=ger,po=3,no=0,pi=2,ni=0,+r]
gram: ger_2s3p_refl [tm=ger,po=3,no=1,pi=2,ni=0,+r]
gram: ger_33s [tm=ger,po=3,no=0,pi=3,-r]
gram: ger_33p [tm=ger,po=3,no=1,pi=3,-r]

### FUNCTIONS
## Accent
# vos with one suffix
func: accent_last n=2, acc=2
# irr1 verbs: dé, sé; accent (insert) é with one suffix
func: accent_irr1 n=1, ins='é'
## Deaccent
# tú, usted(es), nosotros, vosotros, gerund, irr2
func: deacc_first n=2, deacc=1
# vos: di/da + 2 or 3 suffixes
func: deacc_second n=2, deacc=2
# nosotros + s before nos/se
func: mosnos n=2, deacc=1, ins='s'
# irr2, inf
func: deacc_mid n=3, deacc=2

### SUFFIXES
pos: v
## ONE ONLY
# 3rd person
suf: lo +lo
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_3s
  # vos
  pat=vos_grp; change=accent_last; gram=vos_ipv_3s
  pat=vos1; gram=vos_ipv_3s
  # usted
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3s
  # ustedes
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3s
  # nosotros
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_3s
  # infinitive
  pat=inf; gram=inf_3s
  # gerund
  pat=ger_grp; change=deacc_first; gram=ger_3s
suf: le +le
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_3s
  pat=vos_grp; change=accent_last; gram=vos_ipv_3s
  pat=vos1; gram=vos_ipv_3s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3s
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_3s
  pat=inf; gram=inf_3s
  pat=ger_grp; change=deacc_first; gram=ger_3s
suf: la +la
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_3s
  pat=vos_grp; change=accent_last; gram=vos_ipv_3s
  pat=vos1; gram=vos_ipv_3s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3s
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_3s
  pat=inf; gram=inf_3s
  pat=ger_grp; change=deacc_first; gram=ger_3s
suf: los +los
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_3p
  pat=vos_grp; change=accent_last; gram=vos_ipv_3p
  pat=vos1; gram=vos_ipv_3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3p
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_3p
  pat=inf; gram=inf_3p
  pat=ger_grp; change=deacc_first; gram=ger_3p
suf: las +las
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_3p
  pat=vos_grp; change=accent_last; gram=vos_ipv_3p
  pat=vos1; gram=vos_ipv_3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3p
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_3p
  pat=inf; gram=inf_3p
  pat=ger_grp; change=deacc_first; gram=ger_3p
suf: les +les
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_3p
  pat=vos_grp; change=accent_last; gram=vos_ipv_3p
  pat=vos1; gram=vos_ipv_3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3p
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_3p
  pat=inf; gram=inf_3p
  pat=ger_grp; change=deacc_first; gram=ger_3p
suf: se +se
  # reflexive: only usted(es), infinitive, gerund
  # usted
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_refl
  # ustedes
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_refl
  # infinitive
  pat=inf; gram=inf_refl
  # gerund
  pat=ger_grp; change=deacc_first; gram=ger_refl
# 1 person
suf: me +me
  # nosotros not possible
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_1s
  pat=vos_grp; change=accent_last; gram=vos_ipv_1s
  pat=vos1; gram=vos_ipv_1s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s
  pat=inf; gram=inf_1s
  pat=ger_grp; change=deacc_first; gram=ger_1s
suf: nos +nos
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv_1p
  pat=vos_grp; change=accent_last; gram=vos_ipv_1p
  pat=vos1; gram=vos_ipv_1p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p
  # nosotros (add s)
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_refl
  pat=inf; gram=inf_1p
  pat=ger_grp; change=deacc_first; gram=ger_1p
# 2 person
suf: te +te
  # nosotros, vosotros, usted, ustedes not possible
  pat=vos_grp; change=accent_last; gram=vos_ipv_refl
  pat=inf; gram=inf_2s
  pat=ger_grp; change=deacc_first; gram=ger_2s

## TWO OR MORE

# 1+2 person

suf: teme +te+me
  pat=vos; gram=vos_ipv_1s_refl
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1s_refl
  pat=eir; gram=inf_1s2s
  pat=inf_grp; change=deacc_mid; gram=inf_1s2s
  pat=ger_grp; change=deacc_first; gram=ger_1s2s
suf: tenos +te+nos
  pat=vos; gram=vos_ipv_1p_refl
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1p_refl
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_2s_refl
  pat=eir; gram=inf_1p2s
  pat=inf_grp; change=deacc_mid; gram=inf_1p2s
  pat=ger_grp; change=deacc_first; gram=ger_1p2s

# 3 refl + 1/2
suf: seme +se+me
  pat=irr1; gram=usted_ipv_1s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s_refl
  pat=eir; gram=inf_1s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1s_refl
  pat=ger_grp; change=deacc_first; gram=ger_1s_refl
suf: senos +se+nos
  pat=irr1; gram=usted_ipv_1p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s_refl
  pat=eir; gram=inf_1s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1p_refl
  pat=ger_grp; change=deacc_first; gram=ger_1p_refl
suf: sete +se+te
  pat=eir; gram=inf_2s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_2s_refl
  pat=ger_grp; change=deacc_first; gram=ger_2s_refl

# 1/2 + 3
suf: melo +me+lo
  pat=vos; gram=vos_ipv_1s3s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1s3s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3s
  pat=irr1; gram=usted_ipv_1s3s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3s
  pat=eir; gram=inf_1s3s
  pat=inf_grp; change=deacc_mid; gram=inf_1s3s
  pat=ger_grp; change=deacc_first; gram=ger_1s3s
suf: mela +me+la
  pat=vos; gram=vos_ipv_1s3s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1s3s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3s
  pat=irr1; gram=usted_ipv_1s3s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3s
  pat=eir; gram=inf_1s3s
  pat=inf_grp; change=deacc_mid; gram=inf_1s3s
  pat=ger_grp; change=deacc_first; gram=ger_1s3s
suf: mele +me+le
  pat=vos; gram=vos_ipv_1s3s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1s3s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3s
  pat=irr1; gram=usted_ipv_1s3s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3s
  pat=eir; gram=inf_1s3s
  pat=inf_grp; change=deacc_mid; gram=inf_1s3s
  pat=ger_grp; change=deacc_first; gram=ger_1s3s
suf: melos +me+los
  pat=vos; gram=vos_ipv_1s3p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1s3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3p
  pat=irr1; gram=usted_ipv_1s3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3p
  pat=eir; gram=inf_1s3p
  pat=inf_grp; change=deacc_mid; gram=inf_1s3p
  pat=ger_grp; change=deacc_first; gram=ger_1s3p
suf: melas +me+las
  pat=vos; gram=vos_ipv_1s3p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1s3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3p
  pat=irr1; gram=usted_ipv_1s3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3p
  pat=eir; gram=inf_1s3p
  pat=inf_grp; change=deacc_mid; gram=inf_1s3p
  pat=ger_grp; change=deacc_first; gram=ger_1s3p
suf: meles +me+les
  pat=vos; gram=vos_ipv_1s3p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1s3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3p
  pat=irr1; gram=usted_ipv_1s3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3p
  pat=eir; gram=inf_1s3p
  pat=inf_grp; change=deacc_mid; gram=inf_1s3p
  pat=ger_grp; change=deacc_first; gram=ger_1s3p
suf: noslo +nos+lo
  pat=vos; gram=vos_ipv_1p3s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1p3s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3s
  pat=irr1; gram=usted_ipv_1p3s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3s
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_3s_refl
  pat=eir; gram=inf_1p3s
  pat=inf_grp; change=deacc_mid; gram=inf_1p3s
  pat=ger_grp; change=deacc_first; gram=ger_1p3s
suf: nosla +nos+la
  pat=vos; gram=vos_ipv_1p3s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1p3s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3s
  pat=irr1; gram=usted_ipv_1p3s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3s
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_3s_refl
  pat=eir; gram=inf_1p3s
  pat=inf_grp; change=deacc_mid; gram=inf_1p3s
  pat=ger_grp; change=deacc_first; gram=ger_1p3s
suf: nosle +nos+le
  pat=vos; gram=vos_ipv_1p3s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1p3s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3s
  pat=irr1; gram=usted_ipv_1p3s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3s
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_3s_refl
  pat=eir; gram=inf_1p3s
  pat=inf_grp; change=deacc_mid; gram=inf_1p3s
  pat=ger_grp; change=deacc_first; gram=ger_1p3s
suf: noslos +nos+los
  pat=vos; gram=vos_ipv_1p3p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1p3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3p
  pat=irr1; gram=usted_ipv_1p3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3p
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_3p_refl
  pat=eir; gram=inf_1p3p
  pat=inf_grp; change=deacc_mid; gram=inf_1p3p
  pat=ger_grp; change=deacc_first; gram=ger_1p3p
suf: noslas +nos+las
  pat=vos; gram=vos_ipv_1p3p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1p3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3p
  pat=irr1; gram=usted_ipv_1p3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3p
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_3p_refl
  pat=eir; gram=inf_1p3p
  pat=inf_grp; change=deacc_mid; gram=inf_1p3p
  pat=ger_grp; change=deacc_first; gram=ger_1p3p
suf: nosles +nos+les
  pat=vos; gram=vos_ipv_1p3p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_1p3p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3p
  pat=irr1; gram=usted_ipv_1p3p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3p
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_3p_refl
  pat=eir; gram=inf_1p3p
  pat=inf_grp; change=deacc_mid; gram=inf_1p3p
  pat=ger_grp; change=deacc_first; gram=ger_1p3p
suf: telo +te+lo
  pat=vos; gram=vos_ipv_3s_refl
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_3s_refl
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_2s3s
  pat=eir; gram=inf_2s3s
  pat=inf_grp; change=deacc_mid; gram=inf_2s3s
  pat=ger_grp; change=deacc_first; gram=ger_2s3s
suf: tela +te+la
  pat=vos; gram=vos_ipv_3s_refl
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_3s_refl
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_2s3s
  pat=eir; gram=inf_2s3s
  pat=inf_grp; change=deacc_mid; gram=inf_2s3s
  pat=ger_grp; change=deacc_first; gram=ger_2s3s
suf: tele +te+le
  pat=vos; gram=vos_ipv_3s_refl
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_3s_refl
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_2s3s
  pat=eir; gram=inf_2s3s
  pat=inf_grp; change=deacc_mid; gram=inf_2s3s
  pat=ger_grp; change=deacc_first; gram=ger_2s3s
suf: telos +te+los
  pat=vos; gram=vos_ipv_3p_refl
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_3p_refl
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_2s3p
  pat=eir; gram=inf_2s3p
  pat=inf_grp; change=deacc_mid; gram=inf_2s3p
  pat=ger_grp; change=deacc_first; gram=ger_2s3p
suf: telas +te+las
  pat=vos; gram=vos_ipv_3p_refl
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_3p_refl
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_2s3p
  pat=eir; gram=inf_2s3p
  pat=inf_grp; change=deacc_mid; gram=inf_2s3p
  pat=ger_grp; change=deacc_first; gram=ger_2s3p
suf: teles +te+les
  pat=vos; gram=vos_ipv_3p_refl
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_3p_refl
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv_2s3p
  pat=eir; gram=inf_2s3p
  pat=inf_grp; change=deacc_mid; gram=inf_2s3p
  pat=ger_grp; change=deacc_first; gram=ger_2s3p

# 3 person only
suf: selo +se+lo
  # vos
  pat=vos; gram=vos_ipv_33s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_33s
  # tú
  # usted
  pat=irr1; gram=usted_ipv_3s_refl
  pat=irr1; gram=usted_ipv_33s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_33s
  # ustedes
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_33s
  # nosotros
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_33s
  # infinitive (skipping possibility of reflexive)
  pat=eir; gram=inf_33s
  pat=inf_grp; change=deacc_mid; gram=inf_33s
  # gerund (skipping possibility of reflexive)
  pat=ger_grp; change=deacc_first; gram=ger_33s
suf: sela +se+la
  pat=vos; gram=vos_ipv_33s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_33s
  pat=irr1; gram=usted_ipv_3s_refl
  pat=irr1; gram=usted_ipv_33s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_33s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_33s
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_33s
  pat=eir; gram=inf_33s
  pat=inf_grp; change=deacc_mid; gram=inf_33s
  pat=ger_grp; change=deacc_first; gram=ger_33s
suf: sele +se+le
  pat=vos; gram=vos_ipv_33s
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_33s
  pat=irr1; gram=usted_ipv_3s_refl
  pat=irr1; gram=usted_ipv_33s
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_33s
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_33s
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_33s
  pat=eir; gram=inf_33s
  pat=inf_grp; change=deacc_mid; gram=inf_33s
  pat=ger_grp; change=deacc_first; gram=ger_33s
suf: selos +se+los
  pat=vos; gram=vos_ipv_33p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_33p
  pat=irr1; gram=usted_ipv_3p_refl
  pat=irr1; gram=usted_ipv_33p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_33p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_33p
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_33p
  pat=eir; gram=inf_33p
  pat=inf_grp; change=deacc_mid; gram=inf_33p
  pat=ger_grp; change=deacc_first; gram=ger_33p
suf: selas +se+las
  pat=vos; gram=vos_ipv_33p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_33p
  pat=irr1; gram=usted_ipv_3p_refl
  pat=irr1; gram=usted_ipv_33p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_33p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_33p
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_33p
  pat=eir; gram=inf_33p
  pat=inf_grp; change=deacc_mid; gram=inf_33p
  pat=ger_grp; change=deacc_first; gram=ger_33p
suf: seles +se+les
  pat=vos; gram=vos_ipv_33p
  pat=vos1_grp; change=deacc_second; gram=vos_ipv_33p
  pat=irr1; gram=usted_ipv_3p_refl
  pat=irr1; gram=usted_ipv_33p
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_33p
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_33p
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv_33p
  pat=eir; gram=inf_33p
  pat=inf_grp; change=deacc_mid; gram=inf_33p
  pat=ger_grp; change=deacc_first; gram=ger_33p

# 3 suffixes
# reflexive: only usted(es) (not for -te-, -os-), infinitive, gerund
suf: semelo +se+me+lo
  pat=irr1; gram=usted_ipv_1s3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3s_refl
  pat=eir; gram=inf_1s3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1s3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_1s3s_refl
suf: semela +se+me+la
  pat=irr1; gram=usted_ipv_1s3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3s_refl
  pat=eir; gram=inf_1s3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1s3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_1s3s_refl
suf: semele +se+me+le
  pat=irr1; gram=usted_ipv_1s3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3s_refl
  pat=eir; gram=inf_1s3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1s3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_1s3s_refl
suf: semelos +se+me+los
  pat=irr1; gram=usted_ipv_1s3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3p_refl
  pat=eir; gram=inf_1s3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1s3p_refl
  pat=ger_grp; change=deacc_first; gram=ger_1s3p_refl
suf: semelas +se+me+las
  pat=irr1; gram=usted_ipv_1s3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3p_refl
  pat=eir; gram=inf_1s3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1s3p_refl
  pat=ger_grp; change=deacc_first; gram=ger_1s3p_refl
suf: semeles +se+me+les
  pat=irr1; gram=usted_ipv_1s3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1s3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1s3p_refl
  pat=eir; gram=inf_1s3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1s3p_refl
  pat=ger_grp; change=deacc_first; gram=ger
suf: senoslo +se+nos+lo
  pat=irr1; gram=usted_ipv_1p3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3s_refl
  pat=eir; gram=inf_1p3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1p3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_1p3s_refl
suf: senosla +se+nos+la
  pat=irr1; gram=usted_ipv_1p3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3s_refl
  pat=eir; gram=inf_1p3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1p3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_1p3s_refl
suf: senosle +se+nos+le
  pat=irr1; gram=usted_ipv_1p3s_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3s_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3s_refl
  pat=eir; gram=inf_1p3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1p3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_1p3s_refl
suf: senoslos +se+nos+los
  pat=irr1; gram=usted_ipv_1p3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3p_refl
  pat=eir; gram=inf_1p3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1p3p_refl
  pat=ger_grp; change=deacc_first; gram=ger_1p3p_refl
suf: senoslas +se+nos+las
  pat=irr1; gram=usted_ipv_1p3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3p_refl
  pat=eir; gram=inf_1p3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1p3p_refl
  pat=ger_grp; change=deacc_first; gram=ger_1p3p_refl
suf: senosles +se+nos+les
  pat=irr1; gram=usted_ipv_1p3p_refl
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv_1p3p_refl
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv_1p3p_refl
  pat=eir; gram=inf_1p3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_1p3p_refl
  pat=ger_grp; change=deacc_first; gram=ger_1p3p_refl
suf: setelo +se+te+lo
  pat=eir; gram=inf_2s3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_2s3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_2s3s_refl
suf: setela +se+te+la
  pat=eir; gram=inf_2s3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_2s3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_2s3s_refl
suf: setele +se+te+le
  pat=eir; gram=inf_2s3s_refl
  pat=inf_grp; change=deacc_mid; gram=inf_2s3s_refl
  pat=ger_grp; change=deacc_first; gram=ger_2s3s_refl
suf: setelos +se+te+los
  pat=eir; gram=inf_2s3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_2s3p_refl
  pat=ger_grp; change=deacc_first; gram=ger_2s3p_refl
suf: setelas +se+te+las
  pat=eir; gram=inf_2s3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_2s3p_refl
  pat=ger_grp; change=deacc_first; gram=ger_2s3p_refl
suf: seteles +se+te+les
  pat=eir; gram=inf_2s3p_refl
  pat=inf_grp; change=deacc_mid; gram=inf_2s3p_refl
  pat=ger_grp; change=deacc_first; gram=ger_2s3p_refl


