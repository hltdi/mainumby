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
# infinitive
pat: inf r$
pat: inf_grp ([^e])([áéí])(r)$
pat: eir eír$
# gerund: deaccent penultimate syllable
pat: ger_grp ([áé])(ndo)$

### FEATURE STRUCTURES
# real imperative
gram: vos_ipv [p=2,n=0,tm=ipv,+VOS]
# subjunctive
gram: usted_ipv [p=3,n=0,tm=sbp]
gram: ustedes_ipv [p=3,n=1,tm=sbp]
gram: nosotros_ipv [p=1,n=1,tm=sbp]
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

### SUFFIXES
pos: v
## ONE ONLY
# 3rd person
suf: lo +lo
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  # vos
  pat=vos_grp; change=accent_last; gram=vos_ipv
  # usted
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  # ustedes
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  # nosotros
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  # infinitive
  pat=inf; gram=inf
  # gerund
  pat=ger_grp; change=deacc_first; gram=ger
suf: le +le
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: la +la
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: los +los
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: las +las
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: les +les
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: se +se
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
suf: me +me
  # nosotros not possible
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: nos +nos
  pat=irr1_grp; change=accent_irr1; gram=usted_ipv
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  # nosotros (add s)
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
# 2 person
suf: te +te
  # nosotros, vosotros, usted, ustedes not possible
  pat=vos_grp; change=accent_last; gram=vos_ipv
  pat=inf; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

## TWO OR MORE

# 1+2 person

suf: teme +te+me
  pat=vos; gram=vos_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: tenos +te+nos
  pat=vos; gram=vos_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

# 3 refl + 1/2
suf: seme +se+me
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senos +se+nos
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: sete +se+te
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

# 1/2 + 3
suf: melo +me+lo
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: mela +me+la
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: mele +me+le
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: melos +me+los
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: melas +me+las
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: meles +me+les
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: noslo +nos+lo
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: nosla +nos+la
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: nosle +nos+le
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: noslos +nos+los
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: noslas +nos+las
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: nosles +nos+les
  pat=vos; gram=vos_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=irr1; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: telo +te+lo
  pat=vos; gram=vos_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: tela +te+la
  pat=vos; gram=vos_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: tele +te+le
  pat=vos; gram=vos_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: telos +te+los
  pat=vos; gram=vos_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: telas +te+las
  pat=vos; gram=vos_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: teles +te+les
  pat=vos; gram=vos_ipv
  pat=nosotros_grp; change=deacc_first; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

# 3 person only
suf: selo +se+lo
  # vos
  pat=vos; gram=vos_ipv
  # tú
  # usted
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  # ustedes
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  # nosotros
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  # infinitive
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  # gerund
  pat=ger_grp; change=deacc_first; gram=ger
suf: sela +se+la
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: sele +se+le
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: selos +se+los
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: selas +se+las
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seles +se+les
  pat=vos; gram=vos_ipv
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=nosotros_grp_s; change=mosnos; gram=nosotros_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger

# 3 suffixes
# reflexive: only usted(es) (not for -te-, -os-), infinitive, gerund
suf: semelo +se+me+lo
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semela +se+me+la
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semele +se+me+le
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semelos +se+me+los
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semelas +se+me+las
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: semeles +se+me+les
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senoslo +se+nos+lo
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senosla +se+nos+la
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senosle +se+nos+le
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senoslos +se+nos+los
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senoslas +se+nos+las
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: senosles +se+nos+les
  pat=irr1; gram=usted_ipv
  pat=penult_acc_grp; change=deacc_first; gram=usted_ipv
  pat=ustedes_grp; change=deacc_first; gram=ustedes_ipv
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setelo +se+te+lo
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setela +se+te+la
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setele +se+te+le
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setelos +se+te+los
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: setelas +se+te+las
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
suf: seteles +se+te+les
  pat=eir; gram=inf
  pat=inf_grp; change=deacc_mid; gram=inf
  pat=ger_grp; change=deacc_first; gram=ger
