def calculator():
    print("Простой калькулятор")
    print("Доступные операции: +  -  *  /")
    
    num1 = float(input("Введите первое число: "))
    op = input("Введите операцию: ")
    num2 = float(input("Введите второе число: "))

    if op == "+":
        print("Результат:", num1 + num2)
    elif op == "-":
        print("Результат:", num1 - num2)
    elif op == "*":
        print("Результат:", num1 * num2)
    elif op == "/":
        if num2 != 0:
            print("Результат:", num1 / num2)
        else:
            print("Ошибка: деление на ноль!")
    else:
        print("Неизвестная операция!")

calculator()
