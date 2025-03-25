import sys
import os
import output_code



class Node:
    pass

class Num(Node):
    def __init__(self, value):
        self.value = value

class Var(Node):
    def __init__(self, name):
        self.name = name

class Assign(Node):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

class Math(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class CompoundMath(Node):
    def __init__(self, *operations):
        self.operations = operations

class Func(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Call(Node):
    def __init__(self, function_name, arguments):
        self.function_name = function_name
        self.arguments = arguments

class If(Node):
    def __init__(self, condition, body, elif_conditions=None, else_body=None):
        self.condition = condition
        self.body = body
        self.elif_conditions = elif_conditions if elif_conditions else []
        self.else_body = else_body

class Print(Node):
    def __init__(self, expression):
        self.expression = expression

class Return(Node):
    def __init__(self, expression):
        self.expression = expression

class Text(Node):
    def __init__(self, value):
        self.value = value

class For(Node):
    def __init__(self, variable, start_value, end_value, body):
        self.variable = variable
        self.start_value = start_value
        self.end_value = end_value
        self.body = body

class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class Bool(Node):
    def __init__(self, value):
        if isinstance(value, bool):
            self.value = value
        else:
            raise ValueError("The value must be of type bool")


# Новый класс Input для ввода данных
class Input(Node):
    def __init__(self, prompt=None, input_type=str):
        self.prompt = prompt
        self.input_type = input_type

    def visit(self, interpreter):
        prompt = interpreter.visit(self.prompt) if isinstance(self.prompt, Var) else self.prompt
        user_input = input(prompt) if prompt else input()
        try:
            return self.input_type(user_input)  # Перетворюємо введені дані на вказаний тип
        except ValueError:
            raise ValueError(f"Invalid input: expected {self.input_type.__name__}")

class For(Node):
    def __init__(self, variable, start_value, end_value, body):
        self.variable = variable
        self.start_value = start_value
        self.end_value = end_value
        self.body = body

class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Import(Node):
    def __init__(self, file_name):
        self.file_name = file_name

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def visit(self, node):
        if isinstance(node, Num):
            return node.value
        elif isinstance(node, Var):
            return self.variables.get(node.name)
        elif isinstance(node, Bool):
            return node.value
        elif isinstance(node, Assign):
            value = self.visit(node.value)
            self.variables[node.variable.name] = value
            return value
        elif isinstance(node, Math):
            left = self.visit(node.left)
            right = self.visit(node.right)
            return self.perform_math(left, node.operator, right)
        elif isinstance(node, CompoundMath):
            if len(node.operations) < 3:
                raise Exception("Not enough operations in CompoundMath: minimum 3")
            result = self.visit(node.operations[0])
            for i in range(1, len(node.operations), 2):
                operator = node.operations[i]
                right = self.visit(node.operations[i + 1])
                result = self.perform_math(result, operator, right)
            return result
        elif isinstance(node, Text):
            return node.value
        elif isinstance(node, Func):
            self.functions[node.name] = node  # Сохраняем функцию
        elif isinstance(node, Call):
            function = self.functions[node.function_name]
            args = [self.visit(arg) for arg in node.arguments]
            return self.call_function(function, args)
        elif isinstance(node, If):
            if self.visit(node.condition):
                for stmt in node.body:
                    self.visit(stmt)
            else:
                for elif_condition, elif_body in node.elif_conditions:
                    if self.visit(elif_condition):
                        for stmt in elif_body:
                            self.visit(stmt)
                        return
                if node.else_body:
                    for stmt in node.else_body:
                        self.visit(stmt)
        elif isinstance(node, Print):
            result = self.visit(node.expression)
            print(result)
        elif isinstance(node, Return):
            return self.visit(node.expression)  # Возвращаем значение из функции
        elif isinstance(node, Input):
            return node.visit(self)  # Викликаємо метод visit для Input
        elif isinstance(node, For):
            start_value = self.visit(node.start_value)
            end_value = self.visit(node.end_value)
            for i in range(start_value, end_value + 1):
                self.variables[node.variable.name] = i
                for stmt in node.body:
                    self.visit(stmt)
        elif isinstance(node, While):
            while self.visit(node.condition):
                for stmt in node.body:
                    self.visit(stmt)
        elif isinstance(node, Import):
            # Импорт файла
            import_file_path = os.path.join(os.path.dirname(sys.argv[1]), node.file_name)
            load_code_from_file(import_file_path, self)


    def perform_math(self, left, operator, right):
        # Перевірка типів для операторів порівняння
        if operator in ['==', '!=', '>', '<', '>=', '<=']:
            if isinstance(left, str) or isinstance(right, str):
                raise TypeError(f"Cannot compare {type(left)} and {type(right)}")
        
        # Додавання операторів порівняння
        if operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '>':
            return left > right
        elif operator == '<':
            return left < right
        elif operator == '>=':
            return left >= right
        elif operator == '<=':
            return left <= right
        
        # Математичні операції
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            return left / right
        elif operator == '%':
            return left % right

        raise Exception(f"Unknown operator: {operator}")


    def call_function(self, function, arguments):
        local_vars = {param: arg for param, arg in zip(function.params, arguments)}
        previous_vars = self.variables.copy()
        self.variables.update(local_vars)

        return_value = None
        for stmt in function.body:
            return_value = self.visit(stmt)

        self.variables = previous_vars
        return return_value






# Функция для загрузки и интерпретации кода
def load_code_from_file(file_path, interpreter=None):
    try:
        with open(file_path, 'rb') as file:
            code_bytes = file.read()
        code_str = code_bytes.decode('utf-8', errors='ignore')  # Игнорируем ошибки декодирования
        try:
            code = eval(f'[{code_str}]')  # Преобразование строк в список команд
            if interpreter:
                for stmt in code:
                    if isinstance(stmt, Import):
                        # Рекурсивно загружаем код из импортируемого файла
                        import_file_path = os.path.join(os.path.dirname(file_path), stmt.file_name)
                        load_code_from_file(import_file_path, interpreter)
                    else:
                        interpreter.visit(stmt)
            return code
        except Exception as e:
            print(f"Error executing code from file {file_path}: {e}")
            print(f"Check the syntax and defined variables in the file.")
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)

# Пример использования интерпретатора
interpreter = Interpreter()

# Проверка наличия имени файла в аргументах
if len(sys.argv) < 2:
    print("Error: Please provide a file name to run.")
    sys.exit(1)

file_name = sys.argv[1]  # Имя файла из аргументов командной строки
file_extension = os.path.splitext(file_name)[1]  # Получаем расширение файла

if file_extension == '.hs':
    # Если расширение файла .hs, то выполняем конвертацию
    print(f"Converting file {file_name} to Bin.hts...")
    converter = output_code.Converter_to_HTS_lang(file_name, "Bin.hts")
    converter.convert_code()
    # Загружаем и выполняем код из Bin.hts
    code = load_code_from_file('Bin.hts')
    for stmt in code:
        interpreter.visit(stmt)
elif file_extension == '.hts':
    # Если расширение файла .hts, то сразу выполняем код
    print(f"Run the file {file_name}...")
    code = load_code_from_file(file_name)
    for stmt in code:
        interpreter.visit(stmt)
else:
    print(f"Unknown file extension: {file_extension}. Only .hs and .hts are supported.")





