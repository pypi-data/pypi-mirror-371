import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

import pythoncom
import win32com.client


class ExcelAnalyzer:
    """
    Класс для анализа Excel файлов с использованием pywin32 (COM-интерфейс)
    Работает с Excel через Microsoft Office API
    """

    def __init__(self, file_path: str, visible: bool = False):
        """
        Инициализация с путем к Excel файлу

        Args:
            file_path (str): Путь к Excel файлу
            visible (bool): Показывать ли Excel при работе (по умолчанию False)
        """
        self.file_path = os.path.abspath(file_path)
        self.visible = visible
        self.excel_app = None
        self.workbook = None
        self._initialize_excel()
        self._open_workbook()

    def _initialize_excel(self):
        """Инициализация Excel приложения"""
        try:
            # Инициализация COM
            pythoncom.CoInitialize()

            # Создание экземпляра Excel
            self.excel_app = win32com.client.Dispatch("Excel.Application")
            self.excel_app.Visible = self.visible
            self.excel_app.DisplayAlerts = False

            print(f"✅ Excel приложение запущено (версия: {self.excel_app.Version})")

        except Exception as e:
            raise Exception(f"Ошибка инициализации Excel: {str(e)}")

    def _open_workbook(self):
        """Открывает Excel файл"""
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"Файл не найден: {self.file_path}")

            self.workbook = self.excel_app.Workbooks.Open(self.file_path)
            print(f"✅ Файл успешно открыт: {os.path.basename(self.file_path)}")

        except Exception as e:
            raise Exception(f"Ошибка при открытии файла: {str(e)}")

    def get_sheets_count(self) -> int:
        """Возвращает количество листов в файле"""
        return self.workbook.Worksheets.Count

    def get_sheet_names(self) -> List[str]:
        """Возвращает список названий всех листов"""
        sheet_names = []
        for i in range(1, self.workbook.Worksheets.Count + 1):
            sheet_names.append(self.workbook.Worksheets(i).Name)
        return sheet_names

    def get_sheet_dimensions(self, sheet_name: str = None) -> Dict[str, Tuple[int, int]]:
        """
        Возвращает размеры листов (количество строк и столбцов с данными)

        Args:
            sheet_name (str, optional): Имя конкретного листа

        Returns:
            Dict[str, Tuple[int, int]]: Словарь {имя_листа: (строки, столбцы)}
        """
        dimensions = {}

        if sheet_name:
            sheets_to_check = [sheet_name] if sheet_name in self.get_sheet_names() else []
        else:
            sheets_to_check = self.get_sheet_names()

        for name in sheets_to_check:
            ws = self.workbook.Worksheets(name)

            # Получаем используемый диапазон
            used_range = ws.UsedRange
            if used_range is not None:
                rows = used_range.Rows.Count
                cols = used_range.Columns.Count
            else:
                rows = 0
                cols = 0

            dimensions[name] = (rows, cols)

        return dimensions

    def get_file_metadata(self) -> Dict[str, Any]:
        """Возвращает метаданные файла"""
        file_stats = os.stat(self.file_path)

        metadata = {
            'file_path': self.file_path,
            'file_name': os.path.basename(self.file_path),
            'file_size_bytes': file_stats.st_size,
            'file_size_mb': round(file_stats.st_size / (1024 * 1024), 2),
            'created_time': datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'modified_time': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        }

        # Метаданные из Excel через COM
        try:
            # Встроенные свойства документа
            builtin_props = self.workbook.BuiltinDocumentProperties

            prop_names = {
                'Title': 'title',
                'Author': 'author',
                'Subject': 'subject',
                'Comments': 'description',
                'Keywords': 'keywords',
                'Category': 'category',
                'Company': 'company',
                'Manager': 'manager',
                'Creation Date': 'creation_date',
                'Last Save Time': 'last_save_time',
                'Last Author': 'last_author',
                'Revision Number': 'revision',
                'Application Name': 'application',
                'Security': 'security',
            }

            for prop_name, key in prop_names.items():
                try:
                    prop_value = builtin_props(prop_name).Value
                    if prop_value and str(prop_value).strip():
                        if 'date' in key or 'time' in key:
                            if hasattr(prop_value, 'strftime'):
                                metadata[key] = prop_value.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                metadata[key] = str(prop_value)
                        else:
                            metadata[key] = str(prop_value)
                except:
                    pass  # Пропускаем недоступные свойства

            # Excel специфичные метаданные
            metadata.update({
                'excel_version': self.excel_app.Version,
                'calculation_mode': self._get_calculation_mode(),
                'has_macros': self.workbook.HasVBProject,
                'file_format': self._get_file_format(),
                'is_protected': self.workbook.ProtectStructure or self.workbook.ProtectWindows,
                'sheets_count': self.get_sheets_count(),
            })

        except Exception as e:
            print(f"⚠️ Не удалось получить некоторые метаданные: {str(e)}")

        return metadata

    def _get_calculation_mode(self) -> str:
        """Получает режим вычислений"""
        calc_modes = {
            -4105: 'Automatic',  # xlCalculationAutomatic
            -4135: 'Manual',  # xlCalculationManual
            2: 'Semiautomatic'  # xlCalculationSemiautomatic
        }
        try:
            mode = self.excel_app.Calculation
            return calc_modes.get(mode, f'Unknown ({mode})')
        except:
            return 'Unknown'

    def _get_file_format(self) -> str:
        """Получает формат файла"""
        formats = {
            51: 'Excel 2007-2013 (.xlsx)',
            52: 'Excel 2007-2013 with macros (.xlsm)',
            56: 'Excel 97-2003 (.xls)',
            50: 'Excel 2007-2013 binary (.xlsb)',
        }
        try:
            format_code = self.workbook.FileFormat
            return formats.get(format_code, f'Unknown format ({format_code})')
        except:
            return 'Unknown'

    def get_sheet_metadata(self, sheet_name: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Возвращает метаданные листов

        Args:
            sheet_name (str, optional): Имя конкретного листа

        Returns:
            Dict[str, Dict[str, Any]]: Метаданные каждого листа
        """
        sheet_metadata = {}

        sheets_to_check = [
            sheet_name] if sheet_name and sheet_name in self.get_sheet_names() else self.get_sheet_names()

        for name in sheets_to_check:
            ws = self.workbook.Worksheets(name)

            # Базовая информация
            used_range = ws.UsedRange
            if used_range is not None:
                max_row = used_range.Rows.Count
                max_col = used_range.Columns.Count
                used_cells = used_range.Cells.Count
                range_address = used_range.Address
            else:
                max_row = max_col = used_cells = 0
                range_address = "Нет данных"

            # Дополнительная информация
            sheet_info = {
                'sheet_name': name,
                'max_row': max_row,
                'max_column': max_col,
                'used_cells_count': used_cells,
                'data_range': range_address,
                'sheet_visible': self._get_sheet_visibility(ws),
                'sheet_type': self._get_sheet_type(ws),
                'is_protected': ws.ProtectContents or ws.ProtectDrawingObjects or ws.ProtectScenarios,
                'has_autofilter': ws.AutoFilterMode,
                'zoom_level': ws.Range("A1").Application.ActiveWindow.Zoom if self.visible else "N/A",
                'tab_color': self._get_tab_color(ws),
            }

            # Проверяем наличие объектов
            try:
                sheet_info['charts_count'] = ws.ChartObjects().Count
                sheet_info['shapes_count'] = ws.Shapes.Count
                sheet_info['comments_count'] = ws.Comments.Count
                sheet_info['hyperlinks_count'] = ws.Hyperlinks.Count
            except:
                pass

            # Информация о закрепленных панелях
            try:
                if ws.Application.ActiveWindow.FreezePanes:
                    sheet_info['has_freeze_panes'] = True
                else:
                    sheet_info['has_freeze_panes'] = False
            except:
                sheet_info['has_freeze_panes'] = False

            sheet_metadata[name] = sheet_info

        return sheet_metadata

    def _get_sheet_visibility(self, worksheet) -> str:
        """Получает статус видимости листа"""
        visibility_states = {
            -1: 'Visible',  # xlSheetVisible
            0: 'Hidden',  # xlSheetHidden
            2: 'VeryHidden'  # xlSheetVeryHidden
        }
        try:
            return visibility_states.get(worksheet.Visible, 'Unknown')
        except:
            return 'Unknown'

    def _get_sheet_type(self, worksheet) -> str:
        """Получает тип листа"""
        try:
            type_name = worksheet.Type
            types = {
                -4167: 'Worksheet',  # xlWorksheet
                -4109: 'Chart',  # xlChart
                4: 'DialogSheet',  # xlDialogSheet
                1: 'ExcelMacroSheet',  # xlExcel4MacroSheet
                3: 'ExcelIntlMacroSheet'  # xlExcel4IntlMacroSheet
            }
            return types.get(type_name, f'Unknown ({type_name})')
        except:
            return 'Worksheet'

    def _get_tab_color(self, worksheet) -> str:
        """Получает цвет вкладки листа"""
        try:
            color = worksheet.Tab.Color
            if color == 16777215:  # Белый цвет (по умолчанию)
                return 'Default'
            else:
                return f'RGB({color})'
        except:
            return 'Default'

    def print_summary(self):
        """Выводит подробную сводку о файле"""
        print("=" * 70)
        print("📊 АНАЛИЗ EXCEL ФАЙЛА (через pywin32)")
        print("=" * 70)

        # Основная информация
        print(f"\n📁 Файл: {os.path.basename(self.file_path)}")
        print(f"📄 Количество листов: {self.get_sheets_count()}")

        # Информация о листах
        print(f"\n📋 Листы:")
        dimensions = self.get_sheet_dimensions()
        for i, (name, (rows, cols)) in enumerate(dimensions.items(), 1):
            print(f"  {i}. '{name}' - {rows} строк × {cols} столбцов")

        # Метаданные файла
        print(f"\n💾 Метаданные файла:")
        metadata = self.get_file_metadata()
        print(f"  • Размер: {metadata['file_size_mb']} MB ({metadata['file_size_bytes']} байт)")
        print(f"  • Создан: {metadata['created_time']}")
        print(f"  • Изменен: {metadata['modified_time']}")
        print(f"  • Excel версия: {metadata.get('excel_version', 'N/A')}")
        print(f"  • Формат файла: {metadata.get('file_format', 'N/A')}")
        print(f"  • Режим вычислений: {metadata.get('calculation_mode', 'N/A')}")
        print(f"  • Есть макросы: {'Да' if metadata.get('has_macros') else 'Нет'}")
        print(f"  • Защищена структура: {'Да' if metadata.get('is_protected') else 'Нет'}")

        if metadata.get('author'):
            print(f"  • Автор: {metadata['author']}")
        if metadata.get('title'):
            print(f"  • Заголовок: {metadata['title']}")
        if metadata.get('company'):
            print(f"  • Компания: {metadata['company']}")

        # Детали по листам
        print(f"\n📊 Детальная информация по листам:")
        sheet_meta = self.get_sheet_metadata()
        for name, meta in sheet_meta.items():
            print(f"\n  📋 Лист '{name}':")
            print(f"     • Размеры: {meta['max_row']} × {meta['max_column']}")
            print(f"     • Использованных ячеек: {meta['used_cells_count']}")
            print(f"     • Диапазон данных: {meta['data_range']}")
            print(f"     • Видимость: {meta['sheet_visible']}")
            print(f"     • Тип листа: {meta['sheet_type']}")
            print(f"     • Защищен: {'Да' if meta['is_protected'] else 'Нет'}")
            print(f"     • Цвет вкладки: {meta['tab_color']}")

            if meta.get('has_autofilter'):
                print(f"     • Автофильтр: Да")
            if meta.get('charts_count', 0) > 0:
                print(f"     • Диаграмм: {meta['charts_count']}")
            if meta.get('shapes_count', 0) > 0:
                print(f"     • Фигур/объектов: {meta['shapes_count']}")
            if meta.get('comments_count', 0) > 0:
                print(f"     • Комментариев: {meta['comments_count']}")
            if meta.get('hyperlinks_count', 0) > 0:
                print(f"     • Гиперссылок: {meta['hyperlinks_count']}")
            if meta.get('has_freeze_panes'):
                print(f"     • Закрепленные панели: Да")

    def close(self):
        """Закрывает файл и Excel приложение"""
        try:
            if self.workbook:
                self.workbook.Close(SaveChanges=False)
                print("📁 Файл закрыт")

            if self.excel_app:
                self.excel_app.Quit()
                print("📱 Excel приложение закрыто")

            # Очистка COM
            pythoncom.CoUninitialize()

        except Exception as e:
            print(f"⚠️ Предупреждение при закрытии: {str(e)}")

    def __del__(self):
        """Деструктор - автоматически закрывает приложение"""
        self.close()


# Пример использования
if __name__ == "__main__":
    try:
        # Укажите путь к вашему Excel файлу
        file_path = "example.xlsx"  # Замените на реальный путь

        # Создаем анализатор (visible=True покажет Excel)
        analyzer = ExcelAnalyzer(file_path, visible=False)

        # Выводим полную сводку
        analyzer.print_summary()

        # Или получаем отдельные данные
        print(f"\n🔍 Отдельные методы:")
        print(f"Количество листов: {analyzer.get_sheets_count()}")
        print(f"Названия листов: {analyzer.get_sheet_names()}")
        print(f"Размеры листов: {analyzer.get_sheet_dimensions()}")

        # Закрываем
        analyzer.close()

    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        print("\n💡 Убедитесь что:")
        print("   • Установлен Microsoft Excel")
        print("   • Установлен pywin32: pip install pywin32")
        print("   • Файл существует и не заблокирован другим процессом")
