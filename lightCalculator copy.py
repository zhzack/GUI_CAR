from cmath import pi


class LightCalculator:
    # 固定的常量值
    X0 = 95
    Y0_up = 220
    Y0_dn = 270

    def __init__(self):
        self.Num_All = (4 * self.X0 + 2 * self.Y0_up +
                        2 * self.Y0_dn) * 144 / 10
        self.Arr_all = [None] * round(self.Num_All)
        self._initialize_arr_all()

    def _initialize_arr_all(self):
        a1 = 88 * 144 / 10
        a2 = 178 * 144 / 10
        a3 = 232 * 144 / 10
        a4 = 322 * 144 / 10
        a5 = 536 * 144 / 10
        a6 = 626 * 144 / 10
        a7 = 1144 * 144 / 10
        a8 = 1234 * 144 / 10

        n = 0
        for i in range(round(self.Num_All)):
            if i <= a1 or a2 <= i <= a3 or a4 <= i <= a5 or a6 <= i <= a7 or i >= a8:
                n = n + 1
            if a1 < i < a2 or a3 < i < a4 or a5 < i < a6 or a7 < i < a8:
                n = n + pi
            self.Arr_all[i] = round(n)

    def find_closest_value_index(lst, target):
        # 找到最接近的值
        closest_value = min(lst, key=lambda x: abs(x - target))
        # 返回该值的索引
        return lst.index(closest_value)

    def calculate_point(self, x1, y1):
        if x1 == 0:
            if y1 > 0:
                return self.Y0_up + self.X0
            else:
                return 3 * self.X0 + 2 * self.Y0_up + self.Y0_dn
        elif y1 >= 0 and -self.Y0_up / self.X0 < y1 / x1 <= 0:
            return -self.X0 * y1 / x1
        elif y1 > 0 and (y1 / x1 < -self.Y0_up / self.X0 or y1 / x1 > self.Y0_up / self.X0):
            return self.Y0_up + self.X0 + self.Y0_up * x1 / y1
        elif x1 > 0 and -self.Y0_dn / self.X0 < y1 / x1 < self.Y0_up / self.X0:
            return 2 * (self.Y0_up + self.X0) - self.X0 * y1 / x1
        elif y1 < 0 and (y1 / x1 < -self.Y0_dn / self.X0 or y1 / x1 > self.Y0_dn / self.X0):
            return 3 * self.X0 + 2 * self.Y0_up + self.Y0_dn - self.Y0_dn * x1 / y1
        elif y1 < 0 and 0 < y1 / x1 < self.Y0_up / self.X0:
            return 4 * self.X0 + 2 * (self.Y0_up + self.Y0_dn) - self.X0 * y1 / x1

    def get_num_from_distance(self, x, y):
        dist = self.calculate_point(x, y)
        return dist * 144 / 10

    def calculate_num_led(self, x, y):
        
        target = self.get_num_from_distance(x, y)
        print(target)
        # 找到最接近的值
        closest_value = min(self.Arr_all, key=lambda x: abs(x - target))
        print(closest_value)
        # 返回该值的索引
        return self.Arr_all.index(closest_value)


if __name__ == "__main__":
    # 在主程序运行时执行的代码
    calculator = LightCalculator()
    num = calculator.calculate_num_led(0, 200)
    # num = calculator.get_num_from_distance(120)
    print(num)
