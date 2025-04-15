import os
import ast
import sys
import io



try:
    import pathspec
except ImportError:
    pathspec = None
    print("Для поддержки .gitignore установите пакет 'pathspec' (pip install pathspec).")


def get_functions(filepath):
    """Извлекает имена функций, объявленных на верхнем уровне в файле."""
    try:
        with open(filepath, encoding="utf-8") as f:
            file_content = f.read()
    except Exception as e:
        print(f"Ошибка чтения {filepath}: {e}")
        return []

    try:
        tree = ast.parse(file_content, filename=filepath)
    except SyntaxError as e:
        print(f"Ошибка синтаксиса в {filepath}: {e}")
        return []

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
    return functions


def load_ignore_spec(root):
    """
    Загружает правила игнорирования из .gitignore,
    а также добавляет папку .venv в список игнорируемых объектов.
    """
    patterns = []
    gitignore_file = os.path.join(root, ".gitignore")
    if os.path.isfile(gitignore_file):
        try:
            with open(gitignore_file, encoding="utf-8") as f:
                patterns.extend([line.strip() for line in f if line.strip() and not line.startswith("#")])
        except Exception as e:
            print(f"Не удалось прочитать .gitignore: {e}")

    # Обязательно игнорируем папку .venv, даже если её нет в .gitignore
    if ".venv" not in patterns:
        patterns.append(".venv")

    if ".git" not in patterns:
        patterns.append(".git")

    if pathspec:
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    else:
        return None  # Если pathspec не установлен, правила игнорирования не будут применяться


def print_tree(startpath, spec, root, indent_level=0):
    """
    Рекурсивно обходит директорию и печатает её содержимое в виде дерева.
    Для .py файлов дополнительно выводит имена функций.
    Перед выводом проверяет, не соответствует ли путь правилам игнорирования.
    """
    try:
        items = sorted(os.listdir(startpath))
    except Exception as e:
        print(" " * (indent_level * 4) + f"Ошибка доступа к {startpath}: {e}")
        return

    for index, item in enumerate(items):
        path = os.path.join(startpath, item)
        rel_path = os.path.relpath(path, root)

        # Если установлен spec и текущий путь удовлетворяет правилу игнорирования, пропускаем его
        if spec and spec.match_file(rel_path):
            continue

        is_last = index == len(items) - 1
        prefix = "    " * indent_level + ("└── " if is_last else "├── ")

        if os.path.isdir(path):
            print(f"{prefix}{item}/")
            print_tree(path, spec, root, indent_level + 1)
        elif item.endswith(".py"):
            print(f"{prefix}{item}")
            funcs = get_functions(path)
            for func in funcs:
                func_prefix = "    " * (indent_level + 1) + "├── "
                print(f"{func_prefix}def {func}")
        else:
            print(f"{prefix}{item}")


if __name__ == '__main__':
    # Переопределяем стандартный вывод с кодировкой UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # Определяем корневую директорию как ту, в которой находится данный скрипт
    project_path = os.path.dirname(os.path.abspath(__file__))
    ignore_spec = load_ignore_spec(project_path)
    print_tree(project_path, ignore_spec, project_path)
