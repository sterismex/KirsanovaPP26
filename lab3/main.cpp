#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <string>
#include <mpi.h>


/* Программа читает матрицы из файлов, производит вычисления, 
ставит таймер, результат записывает в новый файл.
Параллельная версия на MPI: матрица A разбивается по строкам,
матрица B рассылается всем процессам целиком.*/


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
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 2) {
        if (rank == 0) {
            std::cerr << "Использование: main.exe <размер_матрицы>" << std::endl;
            std::cerr << "Пример: main.exe 200" << std::endl;
        }
        MPI_Finalize();
        return 1;
    }

    int n = std::stoi(argv[1]);

    if (rank == 0) {
        std::cout << "Размер матрицы: " << n << "x" << n << std::endl;
        std::cout << "Процессов MPI: " << size << std::endl;
    }

    std::string fileA = "data/matrix_a_" + std::to_string(n) + ".txt";
    std::string fileB = "data/matrix_b_" + std::to_string(n) + ".txt";
    std::string fileResult = "results/result_" + std::to_string(n) + ".txt";

 
    MPI_Barrier(MPI_COMM_WORLD);

    // ---- Чтение матриц (только на rank 0) ----
    int nA = 0, nB = 0;
    std::vector<std::vector<int>> A, B;

    if (rank == 0) {
        std::cout << "Чтение матриц..." << std::endl;
        A = readMatrix(fileA, nA);
        B = readMatrix(fileB, nB);
        if (nA != nB || nA != n) {
            std::cerr << "Ошибка: размеры матриц не совпадают!" << std::endl;
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
    }

    // Распространяем размер n на все процессы
    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // ---- Рассылаем матрицу B всем процессам ----
    std::vector<int> Bflat(n * n);
    if (rank == 0) {
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j)
                Bflat[i * n + j] = B[i][j];
    }
    MPI_Bcast(Bflat.data(), n * n, MPI_INT, 0, MPI_COMM_WORLD);

    // ---- Разбиваем строки матрицы A между процессами ----
    int rows_per_proc = n / size;
    int remainder = n % size;
    int my_rows = rows_per_proc + (rank < remainder ? 1 : 0);
    int offset = rank * rows_per_proc + std::min(rank, remainder);

    std::vector<int> Aflat;
    if (rank == 0) {
        Aflat.resize(n * n);
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j)
                Aflat[i * n + j] = A[i][j];
    }

    std::vector<int> myA(my_rows * n);
    std::vector<int> sendcounts(size), displs(size);
    for (int r = 0; r < size; ++r) {
        sendcounts[r] = (rows_per_proc + (r < remainder ? 1 : 0)) * n;
        displs[r] = (r * rows_per_proc + std::min(r, remainder)) * n;
    }

    MPI_Scatterv(Aflat.data(), sendcounts.data(), displs.data(), MPI_INT,
                 myA.data(), my_rows * n, MPI_INT,
                 0, MPI_COMM_WORLD);

    // ---- Локальное умножение ----
    std::vector<int> myC(my_rows * n, 0);

    if (rank == 0) std::cout << "Начало умножения..." << std::endl;

    double t_start = MPI_Wtime();

    for (int i = 0; i < my_rows; ++i) {
        for (int j = 0; j < n; ++j) {
            long long sum = 0;
            for (int k = 0; k < n; ++k)
                sum += myA[i * n + k] * Bflat[k * n + j];
            myC[i * n + j] = static_cast<int>(sum);
        }
    }

    double t_end = MPI_Wtime();
    double my_time = t_end - t_start;

    // ---- Собираем результат на rank 0 ----
    std::vector<int> Cflat;
    if (rank == 0) Cflat.resize(n * n);

    MPI_Gatherv(myC.data(), my_rows * n, MPI_INT,
                Cflat.data(), sendcounts.data(), displs.data(), MPI_INT,
                0, MPI_COMM_WORLD);

    // ---- Master пишет результат и выводит статистику ----
    if (rank == 0) {
        std::vector<std::vector<int>> C(n, std::vector<int>(n));
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j)
                C[i][j] = Cflat[i * n + j];

        writeMatrix(fileResult, C, n);

        // Максимальное время по всем процессам
        double max_time = 0;
        MPI_Reduce(&my_time, &max_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

        long long operations = 2LL * n * n * n;

        std::cout << "Время выполнения: " << max_time << " секунд" << std::endl;
        std::cout << "Количество операций: " << operations << std::endl;
        std::cout << "Результат записан в " << fileResult << std::endl;
    } else {
        double dummy;
        MPI_Reduce(&my_time, &dummy, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    }

    MPI_Finalize();
    return 0;
}