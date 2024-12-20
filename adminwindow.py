import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QListWidget, QTableWidget, QTableWidgetItem, QCalendarWidget,
    QFormLayout, QLineEdit, QFileDialog, QMessageBox, QTextEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox, QListWidgetItem
)
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QIcon
from PyQt6.QtCore import Qt, QRectF, QDate, QTime

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.chart import PieChart, Reference, BarChart

from database import profile_info, add_training, check_trainers, delete_training, \
    get_schedule_id, schedule, check_training_types, check_reservation_status, check_register_date
from ui.windows.basewindow import BaseWindow

class AdminWindow(BaseWindow):

    def init_main_content(self):
        self.layout = self.main_content_layout
        self.clear_layout(self.layout)

        # Панель управления пользователями
        schedule_button = QPushButton("Изменить расписание")
        schedule_button.clicked.connect(self.change_schedule)

        self.layout.setSpacing(1)
        # Статистика системы
        stats = QWidget()
        stats.setFixedSize(500, 300)
        self.stats_layout = QVBoxLayout(stats)
        self.stats_button = QPushButton("Открыть дополнительную статистику")
        self.stats_button.clicked.connect(self.open_stats)

        #stats.setStyleSheet("background-color: #e3e3e3; font-size: 16px; height: 200px;")

        self.layout.addWidget(schedule_button)
        self.layout.addWidget(self.stats_button)
        self.layout.addWidget(stats)

        # Инициализация списка тренировок для удаления
        self.training_list = QListWidget()
        self.training_list.setFixedSize(500, 75)

        # Построение и отображение диаграмм
        self.create_pie_chart()

    def create_pie_chart(self):
        active, canceled, ended, absence = 0, 0, 0, 0
        
        self.statuses = ["Активна", "Отменена", "Завершена", "Неявка"]

        rows = check_reservation_status()

        for status in rows:
            if status[0] == "Активна":
                active += 1
            elif status[0] == "Отменена":
                canceled += 1
            elif status[0] == "Завершена":
                ended += 1
            elif status[0] == "Неявка":
                absence += 1
        
        self.counts = [active, canceled, ended, absence]

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(self.counts, labels=self.statuses, autopct='%1.1f%%', startangle=140)
        ax.set_title("Процентное соотношение статуса заявок")

        self.pie_canvas = FigureCanvas(fig)
        self.stats_layout.addWidget(self.pie_canvas)

    # Функция для создания столбчатой диаграммы
    def create_bar_chart():
        rows = check_register_date()
        dates = [row[0] for row in rows]
        date_counts = {date: dates.count(date) for date in set(dates)}

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(date_counts.keys(), date_counts.values(), color='skyblue')
        ax.set_xlabel("Дата регистрации")
        ax.set_ylabel("Количество пользователей")
        ax.set_title("Регистрации по датам")

        # Сохраняем диаграмму в файл
        bar_chart_path = "bar_chart.png"
        fig.savefig(bar_chart_path)
        plt.close(fig)

        return bar_chart_path

    def open_statistic(self):
        self.clear_layout(self.layout)

        print(check_register_date())



    def change_schedule(self):
        self.open_schedule()

    def open_schedule(self):
        # Переопределение метода для управления расписанием
        super().open_schedule()  # Вызов оригинального метода из родительского класса

        # Панель для управления расписанием
        controls_layout = QVBoxLayout()

        # Поля для ввода данных о тренировке
        self.training_type_box = QComboBox()
        self.training_type_box.setPlaceholderText("Тип тренировки")
        controls_layout.addWidget(QLabel("Тип тренировки:"))
        controls_layout.addWidget(self.training_type_box)
        self.load_train_types() # Загрузка типов тренировок

        # Выпадающий список для выбора тренера
        self.trainer_combo_box = QComboBox()
        self.trainer_combo_box.setPlaceholderText("Выберите тренера")
        controls_layout.addWidget(QLabel("Тренер:"))
        controls_layout.addWidget(self.trainer_combo_box)
        self.load_trainers_from_db()  # Загрузка тренеров из базы данных

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        controls_layout.addWidget(QLabel("Дата:"))
        controls_layout.addWidget(self.date_input)

        self.start_time_input = QTimeEdit(QTime.currentTime())
        controls_layout.addWidget(QLabel("Время начала:"))
        controls_layout.addWidget(self.start_time_input)

        self.end_time_input = QTimeEdit(QTime.currentTime().addSecs(3600))
        controls_layout.addWidget(QLabel("Время окончания:"))
        controls_layout.addWidget(self.end_time_input)

        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(1, 50)
        controls_layout.addWidget(QLabel("Вместимость:"))
        controls_layout.addWidget(self.capacity_input)

        # Кнопка добавления тренировки
        add_button = QPushButton("Добавить тренировку")
        add_button.clicked.connect(self.add_training)
        controls_layout.addWidget(add_button)

        # Список тренировок для удаления
        controls_layout.addWidget(QLabel("Выберите тренировку для удаления:"))
        controls_layout.addWidget(self.training_list)

        delete_button = QPushButton("Удалить тренировку")
        delete_button.setFixedSize(400, 35)
        delete_button.clicked.connect(self.delete_training)
        controls_layout.addWidget(delete_button)

        # Загружаем текущие тренировки
        self.load_training_list()

        # Добавляем панель управления в основной layout
        self.layout.addLayout(controls_layout)


    def load_train_types(self):

        self.training_type_box.clear() # Очистка выпадающего списка

        try:
            types = check_training_types()  # Получение списка тренеров из базы данных

            if not types:
                self.training_type_box.addItem("Нет доступных тренеров")
                self.training_type_box.setEnabled(False)
            else:
                self.training_type_box.setEnabled(True)
                for types_tuple in types:
                    types_dict = {
                        'id': types_tuple[0],
                        'name': types_tuple[1]
                    }
                    full_name = f"{types_dict['name']}"
                    self.training_type_box.addItem(full_name, types_dict)  # 'types_dict' передаётся как data
        except Exception as e:
            print(f"Произошла ошибка при загрузке тренеров: {e}")
            self.training_type_box.addItem("Ошибка загрузки тренеров")
            self.training_type_box.setEnabled(False)

    def load_trainers_from_db(self):

        self.trainer_combo_box.clear()  # Очистка выпадающего списка

        try:
            trainers = check_trainers()  # Получение списка тренеров из базы данных

            if not trainers:
                self.trainer_combo_box.addItem("Нет доступных тренеров")
                self.trainer_combo_box.setEnabled(False)
            else:
                self.trainer_combo_box.setEnabled(True)
                for trainer_tuple in trainers:
                    trainer_dict = {
                        'id': trainer_tuple[0],
                        'name': trainer_tuple[1],
                        'surname': trainer_tuple[2]
                    }
                    full_name = f"{trainer_dict['name']} {trainer_dict['surname']}"
                    self.trainer_combo_box.addItem(full_name, trainer_dict)  # 'trainer_dict' передаётся как data
        except Exception as e:
            print(f"Произошла ошибка при загрузке тренеров: {e}")
            self.trainer_combo_box.addItem("Ошибка загрузки тренеров")
            self.trainer_combo_box.setEnabled(False)

    # Добавление тренировки в расписание
    def add_training(self):

        if not self.training_type_box.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите тренера!")
            return

        if not self.trainer_combo_box.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите тренера!")
            return

        self.trainer_id = self.trainer_combo_box.currentData()["id"]
        self.training_type = self.training_type_box.currentData()["id"]
        self.date = self.date_input.date().toString("yyyy-MM-dd")
        self.start_time = self.start_time_input.time().toString("HH:mm")
        self.end_time = self.end_time_input.time().toString("HH:mm")
        self.capacity = self.capacity_input.value()

        training_data = {
            "training_id": self.training_type,
            "trainer_id": self.trainer_id,  # ID тренера
            "date": self.date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "capacity": self.capacity,
        }



        # Сохранение тренировки в базе данных
        schedule_ID = add_training(self.training_type, self.trainer_id, self.date, self.start_time, self.end_time, self.capacity)
        self.load_schedule_for_day(self.date)
        self.load_training_list()  # Обновляем список тренировок


    def delete_training(self):
        # Удаление выбранной тренировки из расписания
        selected_item = self.training_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для удаления!")
            return

        # Получаем данные о тренировке из выбранного элемента списка
        training_data = selected_item.data(Qt.ItemDataRole.UserRole)

        # Получаем Schedule_ID из базы данных на основе полученных данных о тренировке
        schedule_id = get_schedule_id(
            training_data[3],
            training_data[4],
            training_data[5]
        )
        delete_training(schedule_id)
        self.load_schedule_for_day(QDate.currentDate().toString("yyyy-MM-dd"))
        self.load_training_list()  # Обновляем список тренировок

    def load_schedule_for_day(self, selected_date):
        super().load_schedule_for_day(selected_date)  # Вызов оригинального метода из родительского класса

        #Загружает тренировки на выбранный день и обновляет список для удаления
        self.load_training_list(selected_date)


    def load_training_list(self, date=None):
        # Очистка листа на удаление
        self.training_list.clear()

        # Если дата не передана, используем текущий день
        if date is None:
            date = QDate.currentDate().toString("yyyy-MM-dd")
        else:
            date = date

        # Загрузка тренировок для указанной даты
        trainings = schedule(date)

        # Загружает тренировки для выбранного дня в список удаления
        for training in trainings:
            trainer = f"{training[0]} {training[1]}"
            training_type = training[2]
            start_time = training[4]
            end_time = training[5]
            item_text = f"{start_time} - {end_time}: {training_type} ({trainer})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, training)  # Сохраняем данные тренировки в элементе
            self.training_list.addItem(item)

    def open_stats(self):
        output_file = "statistics.xlsx"

        # Проверка, существует ли файл
        if os.path.exists(output_file):
            reply = QMessageBox.question(
                self,
                "Файл уже существует",
                f"Файл '{output_file}' уже существует. Хотите перезаписать его?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                output_file, _ = QFileDialog.getSaveFileName(
                    self, "Сохранить как", "statistics.xlsx", "Excel Files (*.xlsx)"
                )
                if not output_file:  # Пользователь отменил выбор файла
                    return

        # Создание Excel-файла
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Статистика"

        # Добавляем данные о регистрациях
        rows = check_register_date()
        sheet.append(["Дата регистрации", "Количество пользователей"])
        dates = [row[0] for row in rows]
        date_counts = {date: dates.count(date) for date in set(dates)}

        for date, count in date_counts.items():
            sheet.append([date, count])

        # Добавляем круговую диаграмму
        pie_chart = PieChart()
        labels = Reference(sheet, min_col=1, min_row=2, max_row=len(date_counts) + 1)
        data = Reference(sheet, min_col=2, min_row=1, max_row=len(date_counts) + 1)
        pie_chart.add_data(data, titles_from_data=True)
        pie_chart.set_categories(labels)
        pie_chart.title = "Процентное соотношение регистраций"
        sheet.add_chart(pie_chart, "E2")

        # Добавляем столбчатую диаграмму
        bar_chart = BarChart()
        bar_chart.add_data(data, titles_from_data=True)
        bar_chart.set_categories(labels)
        bar_chart.title = "Регистрации по датам"
        bar_chart.x_axis.title = "Дата"
        bar_chart.y_axis.title = "Количество"
        sheet.add_chart(bar_chart, "E20")

        # Сохраняем Excel-файл
        workbook.save(output_file)

        # Открытие созданного файла
        try:
            if os.name == 'nt':  # Windows
                os.startfile(output_file)
            elif os.name == 'posix':  # macOS / Linux
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", output_file])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {e}")

        print(f"Файл {output_file} успешно создан и открыт.")
