import pandas as pd


CSV_PATH = "run_results/timings.csv"


def main():
    df = pd.read_csv(CSV_PATH, encoding="utf-8")

    df["Размер"] = df["Размер"].astype(int)
    df["Потоки"] = df["Потоки"].astype(int)
    df["Время C++ (сек)"] = df["Время C++ (сек)"].astype(float)
    df["Время Python (сек)"] = df["Время Python (сек)"].astype(float)
    df["Операций"] = df["Операций"].astype(int)

    df_avg = df[df["Запуск"] == "СРЕДНЕЕ"].copy()

    print("| Размер | Потоки | Время Python (сек) | Время C++ (сек) | "
          "Операций | Нс/операцию | Ускорение | Эффективность | Проверка |")
    print("|---|---|---|---|---|---|---|---|---|")

    for n in sorted(df_avg["Размер"].unique()):
        sub = df_avg[df_avg["Размер"] == n].sort_values("Потоки")
        t1 = sub[sub["Потоки"] == 1]["Время C++ (сек)"].values
        t1_val = t1[0] if len(t1) > 0 else None

        for _, row in sub.iterrows():
            threads = int(row["Потоки"])
            t = float(row["Время C++ (сек)"])
            ops = int(row["Операций"])
            ns_per_op = t / ops * 1e9

            if t1_val is not None:
                speedup = t1_val / t
                efficiency = speedup / threads * 100
                speedup_str = f"{speedup:.2f}"
                eff_str = f"{efficiency:.1f}%"
            else:
                speedup_str = "—"
                eff_str = "—"

            print(
                f"| {n} "
                f"| {threads} "
                f"| {row['Время Python (сек)']:.4f} "
                f"| {t:.6f} "
                f"| {ops:,} ".replace(",", " ")
                + f"| {ns_per_op:.4f} "
                f"| {speedup_str} "
                f"| {eff_str} "
                f"| {row['Проверка']} |"
            )


if __name__ == "__main__":
    main()