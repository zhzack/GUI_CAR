import os

def count_lines_in_file(file_path):
    """统计单个 Python 文件的行数"""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        return len(lines)

def count_lines_in_directory(directory_path):
    """统计指定文件夹下所有 Python 文件的代码行数"""
    total_lines = 0
    py_files = [f for f in os.listdir(directory_path) if f.endswith('.py')]

    for py_file in py_files:
        file_path = os.path.join(directory_path, py_file)
        if os.path.isfile(file_path):
            lines = count_lines_in_file(file_path)
            print(f"{py_file}: {lines} lines")
            total_lines += lines

    return total_lines

if __name__ == "__main__":
    current_path = os.path.dirname(os.path.realpath(__file__))
    # directory_path = input("请输入要统计的文件夹路径: ")  # 输入文件夹路径
    total_lines = count_lines_in_directory(current_path)
    print(f"\n总行数: {total_lines} 行")
