## perfecto
haber_ [pos=v,tm=prc,+prf] ; 0=>1 p,n ; // 0
## progresivo
estar_ [pos=v,tm=ger,+prg] ; 0=>1 p,n ; // 0
## perfect progresivo
haber_ estado [pos=v,tm=ger,+prf,+prg] ; 0=>2 p,n ; // 0 1
## futuro con ir a
ir_ a [pos=v,tm=inf,+fut] ; 0=>2 p,n; // 0 1
## reflexivo
# se
se [pos=v,p=3,+rflx] ; // 0
# se estar_[p=3] [pos=v,tm=ger,+rflx]
# se haber_[p=3] [pos=v,tm=prc]
# se haber_[p=3] estado [pos=v,tm=ger,+rflx]
# se ir_[p=3] a [pos=v,tm=inf,+rflx]
se querer_|poder_[p=3] [pos=v,tm=inf,+rflx] ; 1=>2 p,n ; // 0
