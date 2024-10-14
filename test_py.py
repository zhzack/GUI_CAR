def generate_segments(width, height, num_pairs):
    segments = []
    for i in range(num_pairs):
        y_start = i * height if i % 2 == 0 else -(i * height)
        y_end = y_start + height
        # 第一个水平线段
        segments.append(((0, y_start), (width, y_start)))
        # 第二个垂直线段
        segments.append(((width, y_end), (0, y_end)))
    return segments

# 示例用法，生成 6 对“U”形线段：
width = 6
height = 5
num_pairs = 6
segments = generate_segments(width, height, num_pairs)
print(segments)
