#comment
print('Will show up in terminal')
e=1
f="ararar"
h=1.1
g=True
print(f'{e} {f} {g} {h}')
#check variable type
print(type(e))
#
print('change variable types')
e=float(e)
print(e)
e=str(e)
print(e)
e=bool(e)
print(e)
#booleans are binary values
g=False
g=int(g)
print(g)
#variable type can also change through math functions as well
inputVar= input("do you get minimum 1 hour of sleep per day?(yes/no):")
print(f"we now know you [{inputVar}] get 1 hour of sleep per day minimum")
#math
mathvar=2
mathvar2=2
print(mathvar+mathvar2)
mathvar2-=2
print(mathvar2)
mathvar2+=3#or you could just use regular math
mathvar2*=5
mathvar2/=5#if you do division it becomes a float
print(mathvar2)
mathvar**=2
print(mathvar)
mathvar=3
mathvar=mathvar%3
print(mathvar)
mathvar=float(2.49)
mathvar=round(mathvar)
print(mathvar)
mathvar=-6987
print(abs(mathvar))#absolute value
mathvar=2
print(pow(2,9))#exponents, ex: 2^9=512
e=int(1)
f=int(2)
g=int(118)
h=min(e,f,g)
print(h)
h=max(e,f,g)
print(h)
# https://youtu.be/jc7TBgMS_kw?list=PLZPZq0r_RZOOkUQbat8LyQii36cJf2SWT&t=412