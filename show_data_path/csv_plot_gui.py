import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_multiple_curves(curve_list, title='', xlabel='', ylabel=''):
    plt.figure(figsize=(10, 6))
    for curve in curve_list:
        plt.plot(curve['values'], label=curve['name'])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_path_comparison(carsts_x, carsts_y):
    """
    绘制路径对比图像
    :param x_coords: 计算的 X 坐标列表
    :param y_coords: 计算的 Y 坐标列表
    :param carsts_x: CarSts 的 X 坐标列表
    :param carsts_y: CarSts 的 Y 坐标列表
    """
    plt.figure(figsize=(10, 6))
    # plt.plot(x_coords, y_coords, marker='o', label='Computed Path')
    plt.scatter(carsts_x, carsts_y, color='red', label='CarSts Path')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Path Comparison')
    plt.legend()
    plt.grid()
    plt.show()


class CSVPlotterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV列曲线可视化工具")
        self.file_path = ''
        self.df = None
        self.column_vars = []
        self.x_column_var = tk.StringVar()

        # 窗口大小为屏幕一半
        sw, sh = master.winfo_screenwidth(), master.winfo_screenheight()
        master.geometry(f"{sw//2}x{sh//2}")

        # 文件选择按钮
        self.load_button = tk.Button(
            master, text="选择CSV文件", command=self.load_csv)
        self.load_button.pack(pady=5)

        # 起始行输入
        self.range_frame = tk.Frame(master)
        self.range_frame.pack(pady=5)
        tk.Label(self.range_frame, text="起始行 (可选):").grid(row=0, column=0)
        tk.Label(self.range_frame, text="结束行 (可选):").grid(row=0, column=2)
        self.start_entry = tk.Entry(self.range_frame, width=10)
        self.end_entry = tk.Entry(self.range_frame, width=10)
        self.start_entry.grid(row=0, column=1, padx=5)
        self.end_entry.grid(row=0, column=3, padx=5)

        # 滚动区域
        self.scroll_frame = tk.Frame(master)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.canvas = tk.Canvas(self.scroll_frame)
        self.scrollbar = tk.Scrollbar(
            self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绘图按钮
        self.plot_button = tk.Button(
            master, text="绘图", command=self.plot_selected_columns, state=tk.DISABLED)
        self.plot_button.pack(pady=10)

    def load_csv(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")])
        if not self.file_path:
            return
        try:
            self.df = pd.read_csv(self.file_path)
            self.df.dropna(how='all', inplace=True)
        except Exception as e:
            messagebox.showerror("读取错误", f"无法读取CSV文件：{e}")
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.column_vars.clear()
        columns = list(self.df.columns)
        self.x_column_var.set(columns[0])

        # X轴单选
        tk.Label(self.scrollable_frame, text="选择X轴：", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", columnspan=3)
        for idx, col in enumerate(columns):
            tk.Radiobutton(
                self.scrollable_frame, text=col, variable=self.x_column_var, value=col
            ).grid(row=1 + idx // 3, column=idx % 3, sticky="w")

        # Y轴复选
        start_row = (len(columns) // 3) + 2
        tk.Label(self.scrollable_frame, text="选择Y轴（可多选）：", font=(
            "Arial", 10, "bold")).grid(row=start_row, column=0, sticky="w", columnspan=3)
        for idx, col in enumerate(columns):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.scrollable_frame, text=col, variable=var)
            chk.grid(row=start_row + 1 + idx // 3, column=idx %
                     3, sticky="w", padx=5, pady=2)
            self.column_vars.append((col, var))

        self.plot_button.config(state=tk.NORMAL)

    def plot_selected_columns(self):
        if self.df is None:
            messagebox.showerror("错误", "请先加载CSV文件")
            return

        try:
            start_idx = int(self.start_entry.get()
                            ) if self.start_entry.get().strip() else 0
            end_idx = int(self.end_entry.get()
                          ) if self.end_entry.get().strip() else len(self.df)
        except ValueError:
            messagebox.showerror("错误", "起始行/结束行必须是整数")
            return

        x_col = self.x_column_var.get()
        selected_cols = [col for col, var in self.column_vars if var.get()]
        # if not selected_cols:
        #     messagebox.showwarning("提示", "请选择至少一个Y轴列")
        #     return

        # if x_col not in self.df.columns:
        #     messagebox.showerror("错误", f"X轴列 {x_col} 不存在")
        #     return

        keyword = 'CAR_UWB::'
        # keyword = 'CAR_UWB_Copy_1::'
        # 找出所有包含关键字的列
        matched_cols = [col for col in self.df.columns if keyword in col]
        # if not matched_cols:
        #     print(f"未找到包含关键字“{keyword}”的列。")
        #     return

        # # 复制包含的列
        # df_selected = self.df[matched_cols].copy()

        # # 构建新的列名：从 keyword 后截取
        # new_column_names = {
        #     col: col.split(keyword, 1)[-1] for col in matched_cols
        # }

        # df_selected.rename(columns=new_column_names, inplace=True)

        # # 提取指定列
        # # df_selected = self.df[selected_cols].copy()

        # df_selected.dropna(how='all', inplace=True)
        # specific_order = [
        #     "uwb_fob_location_index",
        #     "uwb_fob_location_pdoa01",
        #     "uwb_fob_location_pdoa20",
        #     "uwb_fob_location_pdoa12",
        #     "uwb_fob_location_phi",
        #     "uwb_fob_location_theta",
        #     "uwb_fob_location_distance",
        #     "uwb_fob_location_x",
        #     "uwb_fob_location_y",
        #     "uwb_fob_location_z",
        #     "uwb_fob_location_rssi"
        # ]
        # # 用户自定义顺序
        # if specific_order:
        #     # 确保指定的列顺序是 DataFrame 中存在的列
        #     valid_order = [
        #         col for col in specific_order if col in df_selected.columns]
        #     df_selected = df_selected[valid_order]

        #  # 倒序排列列
        #     # df_selected = df_selected[df_selected.columns[::-1]]

        # # 插入三列全为0的列
        # insert_columns = ["DstPdoaFirst", "DstPdoaSecond", "DstPdoaThird"]
        # for col in insert_columns:
        #     # 在指定位置插入列（"uwb_fob_location_z" 和 "uwb_fob_location_rssi" 之间）
        #     df_selected.insert(df_selected.columns.get_loc(
        #         "uwb_fob_location_z") + 1, col, 0)

        # # 强制将所有列的值转换为整型
        # for col in df_selected.columns:
        #     df_selected[col] = pd.to_numeric(
        #         df_selected[col], errors='coerce').fillna(0).astype(int)

        # # 对特定列进行值的修改：大于0的值前加 "+" 符号
        # columns_to_modify = [
        #     "uwb_fob_location_pdoa01",
        #     "uwb_fob_location_pdoa20",
        #     "uwb_fob_location_pdoa12"
        # ]

        # for col in columns_to_modify:
        #     if col in df_selected.columns:
        #         # df_selected[col] = df_selected[col].apply(lambda x: f"+{x}" if x > 0 else str(x))
        #         # 强制将列转换为整数类型，然后应用 + 符号
        #         df_selected[col] = df_selected[col].astype(
        #             int).apply(lambda x: f"+{x}" if x > 0 else str(x))

        # # 构建输出文件路径：原始文件名 + 后缀

        # suffix = keyword[:-2]+".txt"
        # base, ext = os.path.splitext(self.file_path)
        # output_path = base + suffix

        # # 保存为新的CSV文件
        # df_selected.to_csv(output_path, index=False, header=False)

        # # return
        sub_df = self.df.iloc[start_idx:end_idx]
        curves = []

        for col in selected_cols:
            try:
                values = []
                for _, row in sub_df.iterrows():
                    if pd.isna(row[col]):

                        continue
                    if col == 'car_x':
                        car_x = -float(row[col])+180+99
                        # values.append(car_x)
                    elif col == 'car_y':
                        car_y = -float(row[col])
                        # values.append(car_y)
                    elif col == 'PdoaFirst' or col == 'PdoaSecond' or col == 'PdoaThird':
                        pdoa = float(row[col])
                        if (pdoa > 0 and car_x > 180) or (pdoa < 0 and car_x < 180):
                            values.append(1)
                        else:
                            values.append(0)

                    else:
                        values.append(float(row[col]))

            except Exception as e:
                messagebox.showwarning("警告", f"列 {col} 存在非数值数据或空值，跳过绘图。")
                continue

        try:
            x_values = list(range(len(sub_df))
                            ) if x_col == '' else sub_df[x_col].tolist()
            for c in curves:
                c['values'] = c['values'][:len(x_values)]  # 对齐长度
            plot_multiple_curves(curves, title="多列曲线图", xlabel="Index" if x_col == '' else x_col, ylabel="值")
            # plot_path_comparison(
            #     sub_df[selected_cols[0]].tolist(), sub_df[selected_cols[1]].tolist())
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘图失败：{e}")


# 启动GUI
root = tk.Tk()
app = CSVPlotterApp(root)
root.mainloop()
