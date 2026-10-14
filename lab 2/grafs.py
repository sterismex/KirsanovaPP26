import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

CSV_PATH = "run_results/timings.csv"
OUTPUT_DIR = "run_results"


def save_and_close(filename):
    path = f"{OUTPUT_DIR}/{filename}"
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Сохранён: {path}")


def main():
    df = pd.read_csv(CSV_PATH, encoding="utf-8")

    df["Размер"] = df["Размер"].astype(int)
    df["Потоки"] = df["Потоки"].astype(int)
    df["Время C++ (сек)"] = df["Время C++ (сек)"].astype(float)

    df_avg = df[df["Запуск"] == "СРЕДНЕЕ"].copy()

    sizes = sorted(df_avg["Размер"].unique())
    threads_all = sorted(df_avg["Потоки"].unique())

    # ---- График 1: время от потоков для каждого размера ----
    plt.figure(figsize=(10, 6))
    for n in sizes:
        sub = df_avg[df_avg["Размер"] == n].sort_values("Потоки")
        plt.plot(sub["Потоки"], sub["Время C++ (сек)"],
                 "o-", label=f"n={n}", linewidth=2, markersize=8)
    plt.xlabel("Число потоков", fontsize=12)
    plt.ylabel("Время (сек)", fontsize=12)
    plt.title("Время умножения от числа потоков", fontsize=13)
    plt.yscale("log")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=10)
    save_and_close("graph1_time_vs_threads.png")

    # ---- График 2: ускорение от потоков ----
    plt.figure(figsize=(10, 6))
    for n in sizes:
        sub = df_avg[df_avg["Размер"] == n].sort_values("Потоки")
        t1 = sub[sub["Потоки"] == 1]["Время C++ (сек)"].values
        if len(t1) == 0:
            continue
        speedup = t1[0] / sub["Время C++ (сек)"].values
        plt.plot(sub["Потоки"], speedup, "o-", label=f"n={n}",
                 linewidth=2, markersize=8)

    # Идеальное ускорение
    plt.plot(threads_all, threads_all, "k--", label="Идеальное S(p)=p", linewidth=2)

    plt.xlabel("Число потоков", fontsize=12)
    plt.ylabel("Ускорение S(p)", fontsize=12)
    plt.title("Ускорение от числа потоков", fontsize=13)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=10)
    save_and_close("graph2_speedup.png")

    # ---- График 3: эффективность от потоков ----
    plt.figure(figsize=(10, 6))
    for n in sizes:
        sub = df_avg[df_avg["Размер"] == n].sort_values("Потоки")
        t1 = sub[sub["Потоки"] == 1]["Время C++ (сек)"].values
        if len(t1) == 0:
            continue
        speedup = t1[0] / sub["Время C++ (сек)"].values
        efficiency = speedup / sub["Потоки"].values * 100
        plt.plot(sub["Потоки"], efficiency, "o-", label=f"n={n}",
                 linewidth=2, markersize=8)

    plt.axhline(y=100, color="k", linestyle="--", label="Идеал 100%")

    plt.xlabel("Число потоков", fontsize=12)
    plt.ylabel("Эффективность E(p), %", fontsize=12)
    plt.title("Эффективность параллелизации от числа потоков", fontsize=13)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=10)
    save_and_close("graph3_efficiency.png")

    # ---- График 4: производительность (GFLOPS) от потоков ----
    plt.figure(figsize=(10, 6))
    for n in sizes:
        sub = df_avg[df_avg["Размер"] == n].sort_values("Потоки")
        flops = 2 * sub["Размер"].values ** 3
        gflops = flops / (sub["Время C++ (сек)"].values * 1e9)
        plt.plot(sub["Потоки"], gflops, "o-", label=f"n={n}",
                 linewidth=2, markersize=8)

    plt.xlabel("Число потоков", fontsize=12)
    plt.ylabel("Производительность (GFLOPS)", fontsize=12)
    plt.title("Производительность от числа потоков", fontsize=13)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=10)
    save_and_close("graph4_gflops.png")

    print("\nГотово! Все графики сохранены в", OUTPUT_DIR)


if __name__ == "__main__":
    main()