import subprocess
import time
import os
import re
import csv
import numpy as np

SIZES = [200, 400, 800, 1200, 1600, 2000]   
REPEATS = 3                                  # для чистоты эксперемента, возможно, следовало сделать больше, но мне так жалко ноут
EXE_PATH = "./main.exe"                      # путь к скомпилированной C++ программе
DATA_DIR = "data"                            # папка с исходными матрицами
RESULTS_DIR = "results"                      # папка с результатами C++
OUTPUT_DIR = "run_results"             # папка для CSV



def run_cpp(n):
    """
    Запускает C++ программу и возвращает кортеж:
    (время_python(то бишь время работы всей программы), время_cpp(время работы самого алгоритма), stdout, stderr)
    """
    py_start = time.perf_counter()
    result = subprocess.run(
        [EXE_PATH, str(n)],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    py_elapsed = time.perf_counter() - py_start

    if result.returncode != 0:
        return None, None, result.stdout, result.stderr

    #парсим строку "Время выполнения: X секунд"
    cpp_elapsed = None
    match = re.search(r"Время выполнения:\s*([\d.eE+-]+)", result.stdout)
    if match:
        try:
            cpp_elapsed = float(match.group(1))
        except ValueError:
            cpp_elapsed = None

    return py_elapsed, cpp_elapsed, result.stdout, result.stderr


def read_matrix_from_file(filename):
    """Читает матрицу из файла в numpy-массив."""
    with open(filename, "r") as f:
        n = int(f.readline().strip())
        matrix = np.zeros((n, n), dtype=np.int64)
        for i in range(n):
            row = f.readline().strip().split()
            matrix[i] = [int(x) for x in row]
    return matrix


def verify_result(n):
    """
    Проверяет результат программы main.exe C++ через NumPy.
    Возвращает (bool_ok, message, stats),
    где stats — словарь с метриками погрешности.
    """
    file_a = f"{DATA_DIR}/matrix_a_{n}.txt"
    file_b = f"{DATA_DIR}/matrix_b_{n}.txt"
    file_c = f"{RESULTS_DIR}/result_{n}.txt"

    if not (os.path.exists(file_a) and os.path.exists(file_b) and os.path.exists(file_c)):
        return False, "файлы не найдены", {}

    A = read_matrix_from_file(file_a)
    B = read_matrix_from_file(file_b)
    C_cpp = read_matrix_from_file(file_c)

    
    C_numpy = A @ B

    #абсолютная разница
    diff = np.abs(C_cpp - C_numpy)
    max_abs_error = int(diff.max())
    mean_abs_error = float(diff.mean())

    #относительная погрешность
    denom = np.maximum(np.abs(C_numpy), 1)
    rel_error = diff / denom
    max_rel_error = float(rel_error.max())
    mean_rel_error = float(rel_error.mean())

    
    if np.array_equal(C_cpp, C_numpy):
        ok = True
        message = "OK"
    else:
        ok = False
        message = f"РАСХОЖДЕНИЕ (макс. абс.: {max_abs_error})"

    stats = {
        "max_abs_error": max_abs_error,
        "mean_abs_error": mean_abs_error,
        "max_rel_error": max_rel_error,
        "mean_rel_error": mean_rel_error,
    }
    return ok, message, stats


def format_seconds(seconds):
    """Форматирует время в читабельный вид."""
    if seconds is None:
        return "N/A"
    if seconds < 1.0:
        return f"{seconds * 1000:.3f} мс"
    return f"{seconds:.4f} сек"


def main():
    print("=" * 70)
    print("ПРОВЕРКА УМНОЖЕНИЯ МАТРИЦ")
    print("=" * 70)
    print(f"Размеры: {SIZES}")
    print(f"Повторов на размер: {REPEATS}")
    print(f"Программа: {EXE_PATH}")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "timings.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "Размер", "Запуск",
            "Время Python (сек)", "Время C++ (сек)",
            "Операций", "Проверка",
            "Макс. абс. погрешность", "Средняя абс. погрешность",
            "Макс. отн. погрешность", "Средняя отн. погрешность"
        ])

        for n in SIZES:
            print(f"\n--- Размер {n}x{n} ---")

            
            file_a = f"{DATA_DIR}/matrix_a_{n}.txt"
            file_b = f"{DATA_DIR}/matrix_b_{n}.txt"
            if not os.path.exists(file_a) or not os.path.exists(file_b):
                print(f"  Пропуск: нет файлов {file_a} или {file_b}")
                continue

            py_times = []
            cpp_times = []

            
            for i in range(REPEATS):
                print(f"  Запуск {i+1}/{REPEATS}...", end=" ", flush=True)
                py_elapsed, cpp_elapsed, stdout, stderr = run_cpp(n)

                if py_elapsed is None:
                    print("ОШИБКА")
                    print(f"    stderr: {stderr.strip()}")
                    continue

                py_times.append(py_elapsed)
                if cpp_elapsed is not None:
                    cpp_times.append(cpp_elapsed)

                print(
                    f"Python: {format_seconds(py_elapsed)} | "
                    f"C++: {format_seconds(cpp_elapsed)}"
                )
                writer.writerow([
                    n, i + 1,
                    f"{py_elapsed:.6f}",
                    f"{cpp_elapsed:.6f}" if cpp_elapsed is not None else "",
                    2 * n ** 3,
                    "",
                    "", "", "", ""
                ])

            if not py_times:
                continue

            
            print(f"  Проверка точности...", end=" ", flush=True)
            ok, message, stats = verify_result(n)
            print(message)
            if stats:
                print(f"    Макс. абс. погрешность:   {stats['max_abs_error']}")
                print(f"    Средняя абс. погрешность: {stats['mean_abs_error']:.4e}")
                print(f"    Макс. отн. погрешность:   {stats['max_rel_error']:.4e}")
                print(f"    Средняя отн. погрешность: {stats['mean_rel_error']:.4e}")

            
            py_avg = np.mean(py_times)
            py_min = np.min(py_times)
            py_max = np.max(py_times)

            cpp_avg = np.mean(cpp_times) if cpp_times else None
            cpp_min = np.min(cpp_times) if cpp_times else None
            cpp_max = np.max(cpp_times) if cpp_times else None

            print(f"  Python:  среднее {format_seconds(py_avg)} "
                  f"(мин {format_seconds(py_min)}, макс {format_seconds(py_max)})")
            if cpp_avg is not None:
                print(f"  C++:     среднее {format_seconds(cpp_avg)} "
                      f"(мин {format_seconds(cpp_min)}, макс {format_seconds(cpp_max)})")

            
            writer.writerow([
                n, "СРЕДНЕЕ",
                f"{py_avg:.6f}",
                f"{cpp_avg:.6f}" if cpp_avg is not None else "",
                2 * n ** 3,
                message,
                stats.get("max_abs_error", ""),
                f"{stats.get('mean_abs_error', 0):.6e}",
                f"{stats.get('max_rel_error', 0):.6e}",
                f"{stats.get('mean_rel_error', 0):.6e}"
            ])
            writer.writerow([
                n, "МИНИМУМ",
                f"{py_min:.6f}",
                f"{cpp_min:.6f}" if cpp_min is not None else "",
                2 * n ** 3,
                "", "", "", "", ""
            ])
            writer.writerow([
                n, "МАКСИМУМ",
                f"{py_max:.6f}",
                f"{cpp_max:.6f}" if cpp_max is not None else "",
                2 * n ** 3,
                "", "", "", "", ""
            ])

    print("\n" + "=" * 70)
    print(f"Готово! Результаты сохранены в {csv_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()