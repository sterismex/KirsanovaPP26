import re

def parse_log(filename="log.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    pattern = r"Запуск: Размер (\d+), Процессов (\d+).*?Время выполнения: ([\d.]+) секунд"
    matches = re.findall(pattern, text, re.DOTALL)

    data = {}
    for size, procs, time_val in matches:
        size, procs, time_val = int(size), int(procs), float(time_val)
        if size not in data:
            data[size] = {}
        data[size][procs] = time_val
    return data

def main():
    data = parse_log()

    lines = []
    lines.append("| Размер | Процессов | Время (сек) | Операций | Нс/операцию | Ускорение | Эффективность |")
    lines.append("|---|---|---|---|---|---|---|")

    for size in sorted(data.keys()):
        t1 = data[size].get(1, None)
        ops = 2 * size**3
        
        for procs in sorted(data[size].keys()):
            t = data[size][procs]
            ns_op = (t / ops) * 1e9
            
            if t1:
                speedup = t1 / t
                efficiency = (speedup / procs) * 100
                speedup_str = f"{speedup:.2f}"
                eff_str = f"{efficiency:.1f}%"
            else:
                speedup_str = "1.00"
                eff_str = "100.0%"
                
            lines.append(f"| {size} | {procs} | {t:.6f} | {ops:,} | {ns_op:.4f} | {speedup_str} | {eff_str} |".replace(",", " "))

    # Выводим в консоль
    print("\n".join(lines))

    # Сохраняем в файл, чтобы удобно копировать в README
    with open("table.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\nТаблица сохранена в table.md")

if __name__ == "__main__":
    main()