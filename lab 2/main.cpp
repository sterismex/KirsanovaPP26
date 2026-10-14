#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <string>
#include <filesystem>
#include <omp.h>

namespace fs = std::filesystem;


std::vector<std::vector<int>> readMatrix(const std::string& filename, int& n) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Ошибка: не удалось открыть файл " << filename << std::endl;
        exit(1);
    }

    file >> n;
    std::vector<std::vector<int>> matrix(n, std::vector<int>(n));

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            file >> matrix[i][j];
        }
    }
    file.close();
    return matrix;
}


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


int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Использование: main.exe <размер_матрицы> <число_потоков>" << std::endl;
        std::cerr << "Пример: main.exe 800 4" << std::endl;
        return 1;
    }

    int n = std::stoi(argv[1]);
    int threads = std::stoi(argv[2]);
    omp_set_num_threads(threads);

    std::cout << "Размер матрицы: " << n << "x" << n << std::endl;
    std::cout << "Потоков: " << threads << std::endl;

    std::string fileA = "data/matrix_a_" + std::to_string(n) + ".txt";
    std::string fileB = "data/matrix_b_" + std::to_string(n) + ".txt";
    std::string fileResult = "results/result_" + std::to_string(n) + ".txt";

    fs::create_directories("results");

    std::cout << "Чтение матриц..." << std::endl;
    int nA = 0, nB = 0;
    auto A = readMatrix(fileA, nA);
    auto B = readMatrix(fileB, nB);

    if (nA != nB || nA != n) {
        std::cerr << "Ошибка: размеры матриц не совпадают!" << std::endl;
        return 1;
    }

    std::vector<std::vector<int>> C(n, std::vector<int>(n, 0));

    std::cout << "Начало умножения..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();

    #pragma omp parallel for
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            int sum = 0;
            for (int k = 0; k < n; ++k) {
                sum += A[i][k] * B[k][j];
            }
            C[i][j] = sum;
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    long long operations = 2LL * n * n * n;

    std::cout << "Время выполнения: " << elapsed.count() << " секунд" << std::endl;
    std::cout << "Количество операций: " << operations << std::endl;

    writeMatrix(fileResult, C, n);
    std::cout << "Результат записан в " << fileResult << std::endl;

    return 0;
}