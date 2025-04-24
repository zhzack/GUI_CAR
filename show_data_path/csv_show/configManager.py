from pathlib import Path
import json

class ConfigManager:
    def __init__(self, path=None):
        # 自动定位当前.py文件所在目录
        base_dir = Path(__file__).resolve().parent
        config_dir = base_dir / "config"
        config_dir.mkdir(exist_ok=True)  # 自动创建 config 文件夹

        self.path = config_dir / "config.json" if path is None else Path(path)
        self._data = self._load()

    def _load(self):
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def update_header_config(self, column_list, x_axis, y_axis_list):
        key = ",".join(sorted(column_list))
        new_entry = {
            "x_axis": x_axis,
            "y_axis": sorted(y_axis_list)  # 保证顺序一致用于比较
        }

        if key not in self._data:
            self._data[key] = [new_entry]
        else:
            # 判断是否已有相同配置
            existing_list = self._data[key]
            for item in existing_list:
                if item["x_axis"] == new_entry["x_axis"] and sorted(item["y_axis"]) == new_entry["y_axis"]:
                    break  # 已存在，不添加
            else:
                existing_list.append(new_entry)  # 不存在则追加

        self.save()

