import pandas as pd

df = pd.read_csv("run_results/timings.csv", encoding="utf-8")

# Оставляем только строки со средними значениями
df_avg = df[df["Запуск"] == "СРЕДНЕЕ"].copy()

df_avg["Размер"] = df_avg["Размер"].astype(int)
df_avg["Время C++ (сек)"] = df_avg["Время C++ (сек)"].astype(float)
df_avg["Время Python (сек)"] = df_avg["Время Python (сек)"].astype(float)
df_avg["Операций"] = df_avg["Операций"].astype(int)

df_avg["Нс/операцию"] = (df_avg["Время C++ (сек)"] / df_avg["Операций"]) * 1e9

print("| Размер | Время Python (сек) | Время C++ (сек) | Операций | Нс/операцию | Проверка |")
print("|---|---|---|---|---|---|")
for _, row in df_avg.iterrows():
    print(
        f"| {int(row['Размер'])} "
        f"| {row['Время Python (сек)']:.4f} "
        f"| {row['Время C++ (сек)']:.6f} "
        f"| {row['Операций']:,} ".replace(",", " ")
        + f"| {row['Нс/операцию']:.4f} "
        f"| {row['Проверка']} |"
    )