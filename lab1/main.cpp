#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <string>
#include <filesystem> 
#include <print>

/* Программа читает матрицы из файлов, производит вычисления, 
ставит таймер, результат записывает в новый файл*/

namespace fs = std::filesystem;

// Функция чтения матрицы из файла
std::vector<std::vector<int>> readMatrix(const std::string& filename, int& n) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Ошибка: не удалось открыть файл " << filename << std::endl;
        exit(1);
    }

    file >> n; // первая строка — размер матрицы
    std::vector<std::vector<int>> matrix(n, std::vector<int>(n));

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            file >> matrix[i][j];
        }
    }
    file.close();
    return matrix;
}

// Функция записи матрицы в файл
void writeMatrix(const std::string& filename, const std::vector<std::vector<int>>& matrix, int n) {
    std::ofstream file(filename);
    file << n << "\n";
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            file << matrix[i][j];
            if (j < n - 1) file << " ";
        }
        file << "\n";
    }
    file.close();
}

int main(int argc, char* argv[]) 
{
    // Проверяем, передан ли размер матрицы как аргумент
    if (argc < 2) {
        std::cerr << "Использование: main.exe <размер_матрицы>" << std::endl;
        std::cerr << "Пример: main.exe 200" << std::endl;
        return 1;
    }

    int n = std::stoi(argv[1]);
    std::println("Размер матрицы: {}x{}", n, n);
    // Пути к файлам
    std::string fileA = "data/matrix_a_" + std::to_string(n) + ".txt";
    std::string fileB = "data/matrix_b_" + std::to_string(n) + ".txt";
    std::string fileResult = "results/result_" + std::to_string(n) + ".txt";

    // Создаем папку results, если её нет
    fs::create_directories("results");

    // Читаем матрицы
    std::println("Чтение матриц...");
    int nA = 0, nB = 0;
    auto A = readMatrix(fileA, nA);
    auto B = readMatrix(fileB, nB);

    if (nA != nB || nA != n) {
        std::cerr << "Ошибка: размеры матриц не совпадают!" << std::endl;
        return 1;
    }

    // Создаем результирующую матрицу
    std::vector<std::vector<int>> C(n, std::vector<int>(n, 0));

    // Запускаем таймер
    std::println ("Начало умножения...");
    auto start = std::chrono::high_resolution_clock::now();

    // Тройной цикл умножения матриц
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            int sum = 0;
            for (int k = 0; k < n; ++k) {
                sum += A[i][k] * B[k][j];
            }
            C[i][j] = sum;
        }
    }

    // Останавливаем таймер
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    // Считаем количество операций
    long long operations = 2LL * n * n * n; // n^3 умножений + n^3 сложений

    // Выводим результаты
    std::println("Время выполнения: {:.6f} секунд", elapsed.count());
    std::println("Количество операций: {}", operations);
    // Записываем результат в файл
    writeMatrix(fileResult, C, n);
    std::println("Результат записан в {}", fileResult);

    std::println ("\nЭто кто-то читает? Если да, то вот анекдот: ");
    std::println ("Штирлиц и Мюллер катались на танке по очереди.\nОчередь редела, но не расходилась.");
    
    return 0;
}