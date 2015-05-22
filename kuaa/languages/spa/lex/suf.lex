### PATTERNS
## vos imp: groups for accenting final syllable before mult suff
pat: vos_grp ([aeiou][^aeiouáéíóú]*?)([aei])$
pat: vos [aeiou]\w*?[áéí]$
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
## vosotros
pat: vosotros_grp_d ([ae])$
pat: vosotros_acc_grp_id ([í])$
pat: vosotros [aei]d$
pat: vosotros_acc_grp_d ([áéí])$
pat: vosotros_acc_grp ([áéí])(d)$
# infinitive
pat: inf r$
pat: inf_grp ([^e])([áéí])(r)$
pat: eir eír$
# gerund: deaccent penultimate syllable
pat: ger_grp ([áé])(ndo)$

### FEATURE STRUCTURES
# real imperative
gram: vos_ipv [sj=[-1,+2,-p],tm=ipv,+VOS]
gram: tu_ipv [sj=[-1,+2,-p],tm=ipv,-VOS]
gram: vosotros_ipv [sj=[-1,+2,+p],tm=ipv,-AL]
# subjunctive
gram: usted_ipv [sj=[-1,-2,-p],tm=sbp]
gram: ustedes_ipv [sj=[-1,-2,+p],tm=sbp]
gram: nosotros_ipv [sj=[+1,-2,+p],tm=sbp]
# infinitive
gram: inf [tm=inf]
# gerund
gram: ger [tm=ger]

### FUNCTIONS
## Accent
# vos with one suffix
func: accent_last n=2, acc=2
# irr1 verbs: dé, sé; accent (insert) é with one suffix
func: accent_irr1 n=1, ins='é'
## Deaccent
# tú, usted(es), nosotros, vosotros, gerund, irr2
func: deacc_first n=2, deacc=1
# nosotros + s before nos/se
func: mosnos n=2, deacc=1, ins='s'
# irr2, inf
func: deacc_mid n=3, deacc=2
# vosotros + d before os
func: deacc_ados n=1, deacc=1, ins='d'
## Insert only
func: ados n=1, ins='d'

### SUFFIXES
pos: v
## ONE ONLY
# 3rd person
suf: lo +lo pronombre de objeto
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  # tú
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  # vos
  pat=vos_grp; change=accent_last; gram=vos_ipv
  # usted
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  # ustedes
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  # nosotros
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  # vosotros
  pat=vosotros; gram=vosotros_ipv
  # infinitive
  pat=inf; gram=inf
  # gerund
  pat=ger_grp; change=deacc_first; gram=ger
suf: le +le pronombre de objeto
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros; gram=vosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: la +la pronombre de objeto
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros; gram=vosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: los +los pronombre de objeto
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros; gram=vosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: las +las pronombre de objeto
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros; gram=vosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: les +les pronombre de objeto
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros; gram=vosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: se +se pronombre de objeto
  # reflexive: only usted(es), infinitive, gerund
  # usted
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  # ustedes
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  # infinitive
  pat=inf; gram=inf
  # gerund
  pat=ger_grp; change=deacc_first; gram=ger
# 1 person
suf: me +me pronombre de objeto
  # nosotros not possible
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=vosotros; gram=vosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: nos +nos pronombre de objeto
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  # nosotros (add s)
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros; gram=vosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
# 2 person
suf: te +te pronombre de objeto
  # nosotros, vosotros, usted, ustedes not possible
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=irr2; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: os +os pronombre de objeto
  # tú, vos, usted, ustedes not possible
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  # vosotros (add d)
  # ad, ed
  pat=vosotros_grp_d; change=ados; gram=vosotros_ipv
  # id
  pat=vosotros_acc_grp_id; change=deacc_ados; gram=vosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

## TWO OR MORE

# 1+2 person

suf: teme +te+me pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: osme +os+me pronombres de objeto
  pat=vosotros_acc_grp_d; change=deacc_ados; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: tenos +te+nos pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: osnos +os+nos pronombres de objeto
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros_acc_grp_d; change=deacc_ados; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

# 3 refl + 1/2
suf: seme +se+me pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senos +se+nos pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: sete +se+te pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seos +se+os pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

# 1/2 + 3
suf: melo +me+lo pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: mela +me+la pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: mele +me+le pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: melos +me+los pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: melas +me+las pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: meles +me+les pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: noslo +nos+lo pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: nosla +nos+la pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: nosle +nos+le pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: noslos +nos+los pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: noslas +nos+las pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: nosles +nos+les pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: telo +te+lo pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: tela +te+la pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: tele +te+le pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: telos +te+los pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: telas +te+las pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: teles +te+les pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: oslo +os+lo pronombres de objeto
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros_acc_grp_d; change=deacc_ados; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: osla +os+la pronombres de objeto
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros_acc_grp_d; change=deacc_ados; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: osle +os+le pronombres de objeto
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros_acc_grp_d; change=deacc_ados; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: oslos +os+los pronombres de objeto
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros_acc_grp_d; change=deacc_ados; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: oslas +os+las pronombres de objeto
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros_acc_grp_d; change=deacc_ados; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: osles +os+les pronombres de objeto
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=vosotros_acc_grp_d; change=deacc_ados; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

# 3 person only
suf: selo +se+lo pronombres de objeto
  # vos
  pat=vos; gram=vos_ipv
  # tú
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  # usted
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  # ustedes
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  # nosotros
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  # vosotros
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  # infinitive
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  # gerund
  pat=ger_grp; change=deacc_first; gram=ger
suf: sela +se+la pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: sele +se+le pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: selos +se+los pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: selas +se+las pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seles +se+les pronombres de objeto
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=irr2_grp; change=deacc_mid; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=tu_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=vosotros_acc_grp; change=deacc_first; gram=vosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

# 3 suffixes
# reflexive: only usted(es) (not for -te-, -os-), infinitive, gerund
suf: semelo +se+me+lo pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semela +se+me+la pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semele +se+me+le pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semelos +se+me+los pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semelas +se+me+las pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semeles +se+me+les pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senoslo +se+nos+lo pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senosla +se+nos+la pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senosle +se+nos+le pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senoslos +se+nos+los pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senoslas +se+nos+las pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senosles +se+nos+les pronombres de objeto
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setelo +se+te+lo pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setela +se+te+la pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setele +se+te+le pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setelos +se+te+los pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setelas +se+te+las pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seteles +se+te+les pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seoslo +se+os+lo pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seosla +se+os+la pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seosle +se+os+le pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seoslos +se+os+los pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seoslas +se+os+las pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seosles +se+os+les pronombres de objeto
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
