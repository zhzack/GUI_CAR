from cmath import pi


X0 = 75

Y0_up = 180

Y0_dn = 230

# 144 light of 1m

Dist_All = 4*X0+2*Y0_up+2*Y0_dn
perled = 130

Num_All = (4*X0+2*Y0_up+2*Y0_dn)*perled/100


Arr_all = [None]*round(Num_All)

a1 = 88*perled/100
a2 = 178*perled/100
a3 = 452*perled/100
a4 = 542*perled/100
a5 = 756*perled/100
a6 = 846*perled/100
a7 = 1144*perled/100
a8 = 1234*perled/100

n = 0

for i in range(round(Num_All)):

    if i <= a1 or a2 <= i <= a3 or a4 <= i <= a5 or a6 <= i <= a7 or i >= a8:

        n = n+1

    if a1 < i < a2 or a3 < i < a4 or a5 < i < a6 or a7 < i < a8:

        n = n+pi

    Arr_all[i] = round(n)
print(Arr_all[round(Num_All-1)])

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

    elif y1 >= 0 and -Y0_up/X0 < y1/x1 <= 0 and x1 < 0:

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


# calculate light start and end dist

def CalculateStartEnd(dist):

    delta = 40  # unit cm

    if dist-delta < 0:

        End = dist+delta

        Start = Dist_All+dist-delta

    elif dist+delta > Dist_All:

        Start = dist-delta

        End = dist+delta-Dist_All

    else:

        Start = dist-delta

        End = dist+delta

    return Start, End


def calculate_start_end_input_xy(x, y):

    # input x y

    Dist = CalculatePoint(x, y)

    # cal start and end dist

    Start, End = CalculateStartEnd(Dist)

    # StartNumh_closest_value = min(Arr_all, key=lambda x: abs(x - Start))
    # EndNumh_closest_value = min(Arr_all, key=lambda x: abs(x - End))
    # StartNumh = Arr_all.index(StartNumh_closest_value)
    # EndNumh = Arr_all.index(EndNumh_closest_value)

    StartNumh = Arr_all[round(Start*perled/100)]

    EndNumh = Arr_all[round(End*perled/100)]
    return StartNumh, EndNumh


print(calculate_start_end_input_xy(0, -300))
