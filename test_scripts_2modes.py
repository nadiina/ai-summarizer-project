from scripts.get_contents import get_contents
from scripts.get_summary import get_summary

if __name__ == "__main__":
    print("Вибери режим:")
    print("1. Згенерувати підсумок")
    print("2. Згенерувати зміст")
    choice = input("Введи 1 або 2: ")

    if choice == "1":
        result = get_summary()
    elif choice == "2":
        result = get_contents()
    else:
        print("Невірний вибір.")
