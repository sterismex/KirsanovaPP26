import re
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Парсим лог и создаем CSV ---
def parse_log(filename="log.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()
    pattern = r"Запуск: Размер (\d+), Процессов (\d+).*?Время выполнения: ([\d.]+) секунд"
    matches = re.findall(pattern, text, re.DOTALL)
    
    rows = []
    for size, procs, time_val in matches:
        rows.append({"Размер": int(size), "Процессы": int(procs), "Время": float(time_val)})
    return pd.DataFrame(rows)

df = parse_log()
df.to_csv("timings.csv", index=False)

sizes = sorted(df["Размер"].unique())
procs_all = sorted(df["Процессы"].unique())

# --- 2. График 1: Время от числа процессов ---
plt.figure(figsize=(10, 6))
for n in sizes:
    sub = df[df["Размер"] == n].sort_values("Процессы")
    plt.plot(sub["Процессы"], sub["Время"], "o-", label=f"n={n}", linewidth=2, markersize=8)
plt.xlabel("Число процессов", fontsize=12)
plt.ylabel("Время (сек)", fontsize=12)
plt.title("Время умножения от числа процессов MPI", fontsize=13)
plt.yscale("log")
plt.grid(True, which="both", alpha=0.3)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig("graph1_time_vs_procs.png", dpi=150)
plt.close()

# --- 3. График 2: Ускорение ---
plt.figure(figsize=(10, 6))
for n in sizes:
    sub = df[df["Размер"] == n].sort_values("Процессы")
    t1 = sub[sub["Процессы"] == 1]["Время"].values
    if len(t1) == 0: continue
    speedup = t1[0] / sub["Время"].values
    plt.plot(sub["Процессы"], speedup, "o-", label=f"n={n}", linewidth=2, markersize=8)
plt.plot(procs_all, procs_all, "k--", label="Идеальное S(p)=p", linewidth=2)
plt.xlabel("Число процессов", fontsize=12)
plt.ylabel("Ускорение S(p)", fontsize=12)
plt.title("Ускорение от числа процессов MPI", fontsize=13)
plt.grid(True, which="both", alpha=0.3)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig("graph2_speedup.png", dpi=150)
plt.close()

# --- 4. График 3: Эффективность ---
plt.figure(figsize=(10, 6))
for n in sizes:
    sub = df[df["Размер"] == n].sort_values("Процессы")
    t1 = sub[sub["Процессы"] == 1]["Время"].values
    if len(t1) == 0: continue
    speedup = t1[0] / sub["Время"].values
    efficiency = speedup / sub["Процессы"].values * 100
    plt.plot(sub["Процессы"], efficiency, "o-", label=f"n={n}", linewidth=2, markersize=8)
plt.axhline(y=100, color="k", linestyle="--", label="Идеал 100%")
plt.xlabel("Число процессов", fontsize=12)
plt.ylabel("Эффективность E(p), %", fontsize=12)
plt.title("Эффективность параллелизации MPI", fontsize=13)
plt.grid(True, which="both", alpha=0.3)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig("graph3_efficiency.png", dpi=150)
plt.close()

# --- 5. График 4: Производительность (GFLOPS) ---
plt.figure(figsize=(10, 6))
for n in sizes:
    sub = df[df["Размер"] == n].sort_values("Процессы")
    flops = 2 * sub["Размер"].values ** 3
    gflops = flops / (sub["Время"].values * 1e9)
    plt.plot(sub["Процессы"], gflops, "o-", label=f"n={n}", linewidth=2, markersize=8)
plt.xlabel("Число процессов", fontsize=12)
plt.ylabel("Производительность (GFLOPS)", fontsize=12)
plt.title("Производительность MPI от числа процессов", fontsize=13)
plt.grid(True, which="both", alpha=0.3)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig("graph4_gflops.png", dpi=150)
plt.close()

print("Готово! Таблица в timings.csv, графики сохранены в папке.")