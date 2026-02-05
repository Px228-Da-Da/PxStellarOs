import re
import ast
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union, Optional
import importlib.util
import os

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

def _find_os_root(start_dir: str) -> str:
    """
    Ищем корень PxStellarOs по наличию bin/dependencies.py
    Работает даже если DSL запускается из apps/local/Vscode/...
    """
    p = os.path.abspath(start_dir)
    while True:
        if os.path.exists(os.path.join(p, "bin", "dependencies.py")):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            raise FileNotFoundError("Не найден корень ОС (нет bin/dependencies.py). Запусти из папки проекта PxStellarOs.")
        p = parent


def _import_symbol_from_file(module_name: str, file_path: str, symbol: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"spec is None for {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    if not hasattr(mod, symbol):
        raise AttributeError(f"{file_path} has no symbol {symbol}")
    return getattr(mod, symbol)


# --- IMPORT FROM SYSTEM PATHS (PxStellarOs) ---
DraggableResizableWindow = None
Input = None
_DTW_IMPORT_ERROR = None
_INPUT_IMPORT_ERROR = None

try:
    OS_ROOT = _find_os_root(os.path.dirname(__file__))

    init_path = os.path.join(OS_ROOT, "bin", "sys", "class_", "win", "init.py")
    input_path = os.path.join(OS_ROOT, "bin", "sys", "class_", "win", "system_class", "styles", "Input.py")

    DraggableResizableWindow = _import_symbol_from_file("px_init", init_path, "DraggableResizableWindow")
except Exception as e:
    DraggableResizableWindow = None  # type: ignore
    _DRW_IMPORT_ERROR = e
else:
    _DRW_IMPORT_ERROR = None

try:
    # Input — твой кастомный виджет из системы
    Input = _import_symbol_from_file("px_input", input_path, "Input")
except Exception as e:
    Input = None  # type: ignore
    _INPUT_IMPORT_ERROR = e
else:
    _INPUT_IMPORT_ERROR = None



# ---------------- DSL AST ----------------
@dataclass
class AppSpec:
    title: str
    size: Tuple[int, int]

@dataclass
class WidgetSpec:
    var_name: str
    widget_type: str
    kwargs: Dict[str, Any]

@dataclass
class AddSpec:
    var_name: str

@dataclass
class AddRowSpec:
    left_var: str
    right_var: str

# --- Value references for event arguments ---
@dataclass(frozen=True)
class LiteralValue:
    value: Any

@dataclass(frozen=True)
class VarRef:
    name: str

@dataclass(frozen=True)
class AttrRef:
    name: str
    attr: str

ValueNode = Union[LiteralValue, VarRef, AttrRef]

@dataclass
class ActionSpec:
    source_var: str     # e.g. btn
    event_name: str     # e.g. click
    action_name: str    # e.g. show_message
    kwargs: Dict[str, ValueNode]


# ---------------- Parser ----------------
APP_RE = re.compile(r'^\s*app\s+"([^"]+)"\s+size\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$')
ASSIGN_RE = re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*\((.*)\)\s*$')
ADD_RE = re.compile(r'^\s*add\(\s*([A-Za-z_]\w*)\s*\)\s*$')
ADDROW_RE = re.compile(r'^\s*add_row\(\s*([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*\)\s*$')
EVENT_RE = re.compile(r'^\s*([A-Za-z_]\w*)\s*\.\s*(click)\s*->\s*([A-Za-z_]\w*)\s*\((.*)\)\s*$')


def _parse_widget_kwargs(arg_str: str) -> Dict[str, Any]:
    arg_str = arg_str.strip()
    if not arg_str:
        return {}
    node = ast.parse(f"f({arg_str})", mode="eval")
    if not isinstance(node.body, ast.Call):
        raise ValueError("Неверный список аргументов")
    out: Dict[str, Any] = {}
    for kw in node.body.keywords:
        if kw.arg is None:
            raise ValueError("**kwargs не поддерживаются в DSL")
        out[kw.arg] = _safe_literal(kw.value)
    return out


def _parse_action_kwargs(arg_str: str) -> Dict[str, ValueNode]:
    arg_str = arg_str.strip()
    if not arg_str:
        return {}
    node = ast.parse(f"f({arg_str})", mode="eval")
    if not isinstance(node.body, ast.Call):
        raise ValueError("Неверный список аргументов (action)")
    out: Dict[str, ValueNode] = {}
    for kw in node.body.keywords:
        if kw.arg is None:
            raise ValueError("**kwargs не поддерживаются в DSL (action)")
        out[kw.arg] = _value_node(kw.value)
    return out


def _safe_literal(v: ast.AST) -> Any:
    if isinstance(v, (ast.Constant, ast.Tuple, ast.List, ast.Dict)):
        return ast.literal_eval(v)
    if isinstance(v, ast.Name):
        return v.id
    raise ValueError(f"Недопустимое значение аргумента: {ast.dump(v)}")


def _value_node(v: ast.AST) -> ValueNode:
    if isinstance(v, (ast.Constant, ast.Tuple, ast.List, ast.Dict)):
        return LiteralValue(ast.literal_eval(v))
    if isinstance(v, ast.Name):
        return VarRef(v.id)
    if isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name):
        return AttrRef(v.value.id, v.attr)
    raise ValueError(f"Недопустимое значение в action-аргументе: {ast.dump(v)}")


def parse_hs(text: str) -> Tuple[AppSpec, List[WidgetSpec], List[Union[AddSpec, AddRowSpec]], List[ActionSpec]]:
    app: Optional[AppSpec] = None
    widgets: List[WidgetSpec] = []
    layout_cmds: List[Union[AddSpec, AddRowSpec]] = []
    actions: List[ActionSpec] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        m = APP_RE.match(line)
        if m:
            if app is not None:
                raise ValueError("Команда app может быть только один раз")
            title = m.group(1)
            w = int(m.group(2))
            h = int(m.group(3))
            app = AppSpec(title=title, size=(w, h))
            continue

        m = ASSIGN_RE.match(line)
        if m:
            var_name = m.group(1)
            widget_type = m.group(2)
            args_str = m.group(3)
            kwargs = _parse_widget_kwargs(args_str)
            widgets.append(WidgetSpec(var_name, widget_type, kwargs))
            continue

        m = ADDROW_RE.match(line)
        if m:
            layout_cmds.append(AddRowSpec(m.group(1), m.group(2)))
            continue

        m = ADD_RE.match(line)
        if m:
            layout_cmds.append(AddSpec(m.group(1)))
            continue

        m = EVENT_RE.match(line)
        if m:
            source_var = m.group(1)
            event_name = m.group(2)
            action_name = m.group(3)
            args_str = m.group(4)
            kwargs = _parse_action_kwargs(args_str)
            actions.append(ActionSpec(source_var, event_name, action_name, kwargs))
            continue

        raise ValueError(f"Не понимаю строку: {raw_line}")

    if app is None:
        raise ValueError('Нет строки app "..." size(w,h)')

    return app, widgets, layout_cmds, actions


# ---------------- Runtime (PyQt6) ----------------
def _resolve_value(node: ValueNode, objects: Dict[str, Any]) -> Any:
    if isinstance(node, LiteralValue):
        return node.value

    if isinstance(node, VarRef):
        obj = objects.get(node.name)
        if obj is None:
            raise ValueError(f"Неизвестная переменная: {node.name}")
        return obj

    if isinstance(node, AttrRef):
        obj = objects.get(node.name)
        if obj is None:
            raise ValueError(f"Неизвестная переменная: {node.name}")

        if node.attr == "value":
            # твои Input/InputPassword наследуются от QLineEdit, поэтому это работает
            if isinstance(obj, QLineEdit):
                return obj.text()
            if isinstance(obj, QLabel):
                return obj.text()
            if hasattr(obj, "text") and callable(getattr(obj, "text")):
                return obj.text()
            raise ValueError(f"{node.name}.value не поддерживается для {type(obj).__name__}")

        if node.attr == "text":
            if hasattr(obj, "text") and callable(getattr(obj, "text")):
                return obj.text()
            raise ValueError(f"{node.name}.text не поддерживается для {type(obj).__name__}")

        raise ValueError(f"Неизвестный атрибут: {node.name}.{node.attr}")


def _run_action(action: ActionSpec, objects: Dict[str, Any], window: QWidget) -> None:
    name = action.action_name

    if name == "show_message":
        title = "Message"
        if "title" in action.kwargs:
            title = str(_resolve_value(action.kwargs["title"], objects))
        text = ""
        if "text" in action.kwargs:
            text = str(_resolve_value(action.kwargs["text"], objects))
        QMessageBox.information(window, title, text)
        return

    if name == "set_text":
        if "target" not in action.kwargs or "text" not in action.kwargs:
            raise ValueError("set_text требует target=... и text=...")
        target_node = action.kwargs["target"]
        if not isinstance(target_node, VarRef):
            raise ValueError("set_text target должен быть переменной (например target=title)")
        target = objects.get(target_node.name)
        if target is None:
            raise ValueError(f"Неизвестная переменная target={target_node.name}")

        new_text = str(_resolve_value(action.kwargs["text"], objects))
        if isinstance(target, QLabel):
            target.setText(new_text)
            return
        if isinstance(target, QLineEdit):
            target.setText(new_text)
            return
        raise ValueError(f"set_text не поддерживается для {type(target).__name__}")

    if name == "clear":
        if "target" not in action.kwargs:
            raise ValueError("clear требует target=...")
        target_node = action.kwargs["target"]
        if not isinstance(target_node, VarRef):
            raise ValueError("clear target должен быть переменной (например target=namber)")
        target = objects.get(target_node.name)
        if target is None:
            raise ValueError(f"Неизвестная переменная target={target_node.name}")
        if hasattr(target, "clear") and callable(getattr(target, "clear")):
            target.clear()
            return
        raise ValueError(f"clear не поддерживается для {type(target).__name__}")

    raise ValueError(f"Неизвестное действие: {name}")


def _require_imports() -> None:
    if DraggableResizableWindow is None:
        raise RuntimeError(
            "Не удалось импортировать DraggableResizableWindow из init.py.\n"
            "Положи init.py рядом с dsl_v4.py (или добавь его в PYTHONPATH).\n"
            f"Ошибка импорта: {_DRW_IMPORT_ERROR}"
        )

    if Input is None:
        raise RuntimeError(
            "Не удалось импортировать Input из Input.py.\n"
            "Положи Input.py рядом с dsl_v4.py (или добавь его в PYTHONPATH).\n"
            f"Ошибка импорта: {_INPUT_IMPORT_ERROR}"
        )

    # InputPassword необязателен, но если используешь в DSL — он должен импортироваться
    # (проверим при создании виджета)


def build_app(app_spec: AppSpec, widget_specs: List[WidgetSpec], layout_cmds: List[Union[AddSpec, AddRowSpec]], actions: List[ActionSpec]) -> QWidget:
    _require_imports()

    window = DraggableResizableWindow(parent=None, window_name=app_spec.title, enable_maximize=True)  # type: ignore
    window.resize(*app_spec.size)

    content = QWidget()
    root = QVBoxLayout(content)
    content.setLayout(root)

    objects: Dict[str, Any] = {}

    # Widget factory
    for ws in widget_specs:
        wt = ws.widget_type

        if wt == "Label":
            text = str(ws.kwargs.get("text", ""))
            obj = QLabel(text)

        elif wt == "Input":
            # --- use user's Input ---
            placeholder = str(ws.kwargs.get("placeholder_text", ""))
            initial = str(ws.kwargs.get("initial_text", ""))
            lang_code = ws.kwargs.get("lang_code", "en")
            translator = ws.kwargs.get("translator", None)

            # echo_mode: можно передать как строку "Password"/"Normal", либо число, либо не передавать
            echo_mode_kw = ws.kwargs.get("echo_mode", None)
            echo_mode = QLineEdit.EchoMode.Normal
            if isinstance(echo_mode_kw, str):
                if echo_mode_kw.lower() == "password":
                    echo_mode = QLineEdit.EchoMode.Password
                elif echo_mode_kw.lower() == "normal":
                    echo_mode = QLineEdit.EchoMode.Normal
            elif isinstance(echo_mode_kw, int):
                try:
                    echo_mode = QLineEdit.EchoMode(echo_mode_kw)
                except Exception:
                    echo_mode = QLineEdit.EchoMode.Normal

            obj = Input(
                parent=None,
                placeholder_text=placeholder,
                initial_text=initial,
                echo_mode=echo_mode,
                translator=translator,
                lang_code=lang_code,
            )  # type: ignore

        elif wt == "InputPassword":
            # --- use user's InputPassword (если есть) ---
            if InputPassword is None:
                raise RuntimeError(
                    "В DSL использован InputPassword(...), но не удалось импортировать InputPassword из InputPassword.py.\n"
                    f"Ошибка импорта: {_INPUT_PW_IMPORT_ERROR}"
                )

            placeholder = str(ws.kwargs.get("placeholder_text", ""))
            initial = str(ws.kwargs.get("initial_text", ""))
            lang_code = ws.kwargs.get("lang_code", "en")
            translator = ws.kwargs.get("translator", None)

            # по умолчанию Password
            echo_mode_kw = ws.kwargs.get("echo_mode", "Password")
            echo_mode = QLineEdit.EchoMode.Password
            if isinstance(echo_mode_kw, str):
                if echo_mode_kw.lower() == "normal":
                    echo_mode = QLineEdit.EchoMode.Normal
                elif echo_mode_kw.lower() == "password":
                    echo_mode = QLineEdit.EchoMode.Password

            obj = InputPassword(
                parent=None,
                placeholder_text=placeholder,
                initial_text=initial,
                echo_mode=echo_mode,
                translator=translator,
                lang_code=lang_code,
            )  # type: ignore

        elif wt == "Button":
            text = str(ws.kwargs.get("text", ""))
            obj = QPushButton(text)

        else:
            raise ValueError(f"Неизвестный виджет: {wt}")

        objects[ws.var_name] = obj

    # Layout commands
    for cmd in layout_cmds:
        if isinstance(cmd, AddSpec):
            if cmd.var_name not in objects:
                raise ValueError(f"add({cmd.var_name}) — такой переменной нет")
            root.addWidget(objects[cmd.var_name])

        elif isinstance(cmd, AddRowSpec):
            if cmd.left_var not in objects:
                raise ValueError(f"add_row({cmd.left_var}, ...) — такой переменной нет")
            if cmd.right_var not in objects:
                raise ValueError(f"add_row(..., {cmd.right_var}) — такой переменной нет")
            row = QHBoxLayout()
            row.addWidget(objects[cmd.left_var])
            row.addWidget(objects[cmd.right_var])
            root.addLayout(row)

        else:
            raise ValueError("Неизвестная layout-команда")

    window.set_content(content)  # type: ignore

    # Events
    for act in actions:
        src = objects.get(act.source_var)
        if src is None:
            raise ValueError(f"Событие: нет переменной {act.source_var}")
        if act.event_name == "click":
            if not isinstance(src, QPushButton):
                raise ValueError(f"{act.source_var}.click поддерживается только для Button")
            src.clicked.connect(lambda _=False, a=act: _run_action(a, objects, window))  # type: ignore
        else:
            raise ValueError(f"Неизвестное событие: {act.event_name}")

    return window


def run_hs_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    app_spec, widget_specs, layout_cmds, actions = parse_hs(text)

    qt_app = QApplication(sys.argv)
    window = build_app(app_spec, widget_specs, layout_cmds, actions)
    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dsl_v4.py <file.hs>")
        raise SystemExit(2)

    run_hs_file(sys.argv[1])
