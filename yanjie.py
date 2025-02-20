# New Cordinate

from cmath import pi


# E5 参数长度=4892mm，宽度=1905mm


X0 = 95

Y0_up = 220

Y0_dn = 270

# 144 light of 1m

Num_All = (4*X0+2*Y0_up+2*Y0_dn)*144/10


Arr_all = [None]*round(Num_All)

a1 = 88*144/10
a2 = 178*144/10
a3 = 232*144/10
a4 = 322*144/10
a5 = 536*144/10
a6 = 626*144/10
a7 = 1144*144/10
a8 = 1234*144/10

n = 0

for i in range(round(Num_All)):

    if i <= a1 or a2 <= i <= a3 or a4 <= i <= a5 or a6 <= i <= a7 or i >= a8:

        n = n+1

    if a1 < i < a2 or a3 < i < a4 or a5 < i < a6 or a7 < i < a8:

        n = n+pi

    Arr_all[i] = round(n)


# input cordinate x,y

def CalculatePoint(x1, y1):

    if x1 == 0:

        if y1 > 0:

            Out = Y0_up+X0

        else:

            Out = 3*X0+2*Y0_up+Y0_dn

    # in section 1: m=y1*n/x1,n=-X0;

    # y1>0, Out=-X0*y1/x1

    # y1<0, Out=4*X0+2*(Y0_up+Y0_dn)-X0*y1/x1

    elif y1 >= 0 and -Y0_up/X0 < y1/x1 <= 0:

        Out = -X0*y1/x1

    # in section 2: m=y1*n/x1,m=Y0_up

    # Out=Y0_up+X0+Y0_up*x1/y1

    elif y1 > 0 and (y1/x1 < -Y0_up/X0 or y1/x1 > Y0_up/X0):

        Out = Y0_up+X0+Y0_up*x1/y1

    # in section 2: m=y1*n/x1,n=X0

    # Out=2*(Y0_up+X0)-X0*y1/x1

    elif x1 > 0 and -Y0_dn/X0 < y1/x1 < Y0_up/X0:

        Out = 2*(Y0_up+X0)-X0*y1/x1

    # in section 2: m=y1*n/x1,m=-Y0_dn

    # Out=3*X0+2*Y0_up+Y0_dn-Y0_dn*x1/y1

    elif y1 < 0 and (y1/x1 < -Y0_dn/X0 or y1/x1 > Y0_dn/X0):

        Out = 3*X0+2*Y0_up+Y0_dn-Y0_dn*x1/y1

    elif y1 < 0 and 0 < y1/x1 < Y0_up/X0:

        Out = 4*X0+2*(Y0_up+Y0_dn)-X0*y1/x1

    return Out


Dist = CalculatePoint(0, 120)

num = Dist*144/10


print(num)
