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
    df["Время C++ (сек)"] = df["Время C++ (сек)"].astype(float)
    df["Время Python (сек)"] = df["Время Python (сек)"].astype(float)

    df_avg = df[df["Запуск"] == "СРЕДНЕЕ"].copy().sort_values("Размер")

    sizes = df_avg["Размер"].values
    time_cpp = df_avg["Время C++ (сек)"].values
    time_py = df_avg["Время Python (сек)"].values

    theory = time_cpp[0] * (sizes ** 3) / (sizes[0] ** 3)

    plt.figure(figsize=(9, 6))
    plt.loglog(sizes, time_cpp, "o-", label="Эксперимент (C++)",
               color="blue", linewidth=2, markersize=8)
    plt.loglog(sizes, theory, "--", label="Теория $O(n^3)$",
               color="red", linewidth=2)

    plt.xlabel("Размер матрицы $n$", fontsize=12)
    plt.ylabel("Время (сек)", fontsize=12)
    plt.title("Зависимость времени умножения от размера (лог-лог)", fontsize=13)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=11)
    save_and_close("graph1_loglog.png")

    flops = 2 * sizes ** 3
    gflops = flops / (time_cpp * 1e9)

    plt.figure(figsize=(9, 6))
    plt.semilogx(sizes, gflops, "o-", color="darkgreen",
                 linewidth=2, markersize=10)

    for x, y in zip(sizes, gflops):
        plt.annotate(f"{y:.2f}", (x, y),
                     textcoords="offset points", xytext=(0, 10),
                     ha="center", fontsize=10)

    mean_gflops = np.mean(gflops)
    plt.axhline(y=mean_gflops, color="red", linestyle="--",
                label=f"Среднее = {mean_gflops:.2f} GFLOPS")

    plt.xlabel("Размер матрицы $n$", fontsize=12)
    plt.ylabel("Производительность (GFLOPS)", fontsize=12)
    plt.title("Производительность умножения матриц от размера", fontsize=13)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=11)
    save_and_close("graph2_performance.png")

    plt.figure(figsize=(9, 6))
    plt.loglog(sizes, time_py, "o-", label="Python (общее время)",
               color="orange", linewidth=2, markersize=8)
    plt.loglog(sizes, time_cpp, "s-", label="C++ (чистое умножение)",
               color="blue", linewidth=2, markersize=8)

    plt.xlabel("Размер матрицы $n$", fontsize=12)
    plt.ylabel("Время (сек)", fontsize=12)
    plt.title("Сравнение замеров: Python vs C++ (лог-лог)", fontsize=13)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(fontsize=11)
    save_and_close("graph3_compare.png")

    print("\nГотово! Все графики сохранены в", OUTPUT_DIR)


if __name__ == "__main__":
    main()