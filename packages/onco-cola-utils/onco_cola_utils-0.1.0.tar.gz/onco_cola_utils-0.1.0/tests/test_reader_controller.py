from pathlib import Path

from src.my_utils.logger import log, loginf
from src.my_utils.reader_controller.core import ReaderController

print = log


def get_curent_path():
    return Path(__file__).resolve().parent


def test_reader_controller_initialization():
    """Проверка инициализации ReaderController"""
    file_path = get_curent_path() / "dummy.xlsx"
    loginf(file_path)
    file_output = get_curent_path() / "output.xlsx"
    loginf(file_output)

    rc = ReaderController(file_path, file_output)

    assert rc._file_path == file_path
    assert rc._file_output == file_output
    assert rc._dataframe == []
    print("✅ ReaderController инициализирован корректно")


def test_rename_method():
    """Проверка метода rename (с mocked путями)"""
    # Важно: не реальный файл, а просто Path-объекты

    file_path = get_curent_path() / "dummy.xlsx"
    loginf(file_path)
    file_output = get_curent_path() / "output.xlsx"
    loginf(file_output)

    rc = ReaderController(
        file_path=file_path,
        file_output=file_output
    )

    # Сохраним старый путь
    old_path = rc._file_path

    # Вызываем rename
    rc.rename("new_file", same_file=True)

    # Проверяем, что путь изменился
    assert rc._file_path.name == "new_file.xlsx"
    assert rc._file_path.parent == old_path.parent

    rc.rename("dummy", same_file=True)

    print("✅ Метод rename работает корректно")


if __name__ == "__main__":
    # Запуск тестов напрямую
    test_reader_controller_initialization()
    test_rename_method()
