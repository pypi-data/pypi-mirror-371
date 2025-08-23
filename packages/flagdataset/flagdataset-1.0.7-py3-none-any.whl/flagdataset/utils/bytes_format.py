def format_bytes(size_bytes):
    """将字节转换为合适的单位"""
    if not isinstance(size_bytes, (int, float)):
        raise TypeError("输入必须是数字类型")

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    index = 0
    size = abs(size_bytes)

    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1

    # 当数值为整数时不显示小数部分
    if size.is_integer():
        return f"{int(size)}{units[index]}"
    return f"{size:.2f}{units[index]}"
