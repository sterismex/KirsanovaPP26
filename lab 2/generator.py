import random
import os
import sys

def generate_and_save_matrix(size, filename):
    """
    Этот код генерирует квадратную матрицу размера n*n 
    и записывает её в файл.
    """

    with open(filename, 'w') as f:

        f.write(f"{size}\n")
        
        for i in range(size):

            row = [str(random.randint(0, 9)) for _ in range(size)]
            
            f.write(" ".join(row) + "\n")

def main():

    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Ошибка: размер должен быть целым числом.")
            return
    else:
        n = 2
    
    print(f"Генерация матриц размером {n}x{n}...")

    os.makedirs("data", exist_ok=True)


    file_a = f"data/matrix_a_{n}.txt"
    file_b = f"data/matrix_b_{n}.txt"


    generate_and_save_matrix(n, file_a)
    generate_and_save_matrix(n, file_b)

    print(f"Готово! Файлы сохранены:")
    print(f" - {file_a}")
    print(f" - {file_b}")

if __name__ == "__main__":
    main()