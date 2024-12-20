import sys
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QTableWidget,
    QPushButton, QFormLayout, QLineEdit, QFileDialog, QListWidgetItem, QMessageBox, QTableWidgetItem,
    QListWidget, QGridLayout, QFrame, QScrollArea, QWidget, QDialog, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QRectF, QDate, QTime, QTimer

import database
from database import profile_info, schedule, check_trainers, check_reservation, change_status, \
    check_attendance, client_id_search
from ui.windows.basewindow import BaseWindow


class ClientWindow(BaseWindow):
    def init_main_content(self):
        self.layout = self.main_content_layout

        self.clear_layout(self.layout)
        
        self.client_id = client_id_search(self.user_login)
        
        # Создание кнопок
        training_button = QPushButton("Записаться на тренировку")
        training_button.clicked.connect(self.open_schedule)

        trainers_button = QPushButton("Посмотреть список тренеров")
        trainers_button.clicked.connect(self.open_trainers_window)

        # Секция с активными записями
        active_label = QLabel("Активные записи")
        active_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        active_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        active_label.setFixedSize(300, 35)

        self.reservations_list = QListWidget()
        self.reservations_list.setFixedSize(500, 100)
        self.reservations_list.setItemAlignment(Qt.AlignmentFlag.AlignCenter)

        # Секция с кнопками истории
        history_layout = QVBoxLayout()
        self.all_reservations_button = QPushButton("История записей")
        self.all_reservations_button.clicked.connect(self.all_attendance)
        history_layout.addWidget(self.all_reservations_button)

        self.attendance_history = QPushButton("История посещений")
        self.attendance_history.clicked.connect(self.load_attendance_history)
        history_layout.addWidget(self.attendance_history)

        # Макет для тренеров
        self.Tscroll_area = QScrollArea()
        self.Tscroll_area.setWidgetResizable(True)
        self.trainers_widget = QWidget()
        self.trainers_layout = QGridLayout(self.trainers_widget)


        # Добавляем верхнюю панель с кнопками
        top_layout = QHBoxLayout()
        top_layout.addWidget(training_button)
        top_layout.addWidget(trainers_button)
        top_layout.addStretch(1)

        self.layout.addLayout(top_layout)  # Добавляем верхнюю панель с кнопками
        self.layout.addWidget(active_label)  # Добавляем заголовок для активных записей
        self.layout.addWidget(self.reservations_list)  # Добавляем сам список
        self.layout.addStretch(1)  # Расстояние до следующих элементов
        self.layout.addLayout(history_layout)  # История посещений и записей

        # Загрузка активных записей
        self.load_active_reservations()

        self.layout.addSpacing(0)

    def load_active_reservations(self):

        self.reservations_list.clear()

        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        current_time = QTime.currentTime().toString("HH:mm")

        reservations = check_reservation(self.user_login)

        for reservation in reservations:
            status = reservation[6]
            day = reservation[8]
            startime = reservation[9]
            endtime = reservation[10]
            type = reservation[11]
            trainer_name = reservation[13]
            trainer_surname = reservation[14]

            is_past = day < current_date or (
                    day == current_date and startime < current_time
            )

            if status == "Активна":
                if is_past == True:
                    change_status("Неявка", self.user_login, reservation[4])
                else:
                    item_text = f"Вы записаны на тренировку {day} {startime} - {endtime} {type} Тренер: {trainer_surname} {trainer_name}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, reservation)  # Сохраняем данные тренировки в элементе
                    self.reservations_list.addItem(item)

        self.reservations_list.itemDoubleClicked.connect(self.handle_item_double_click)

        #print(reservations)
    def all_attendance(self):

        # Очистка текущих виджетов
        self.clear_layout(self.layout)

        # Получение данных о записях пользователя на тренировки
        info = check_reservation(self.user_login)

        # Проверка наличия данных
        if not info:
            print("Нет записей для отображения.")
            return

        # Создание таблицы
        table = QTableWidget()
        table.setRowCount(len(info))  # Устанавливаем количество строк
        table.setColumnCount(6)  # Количество столбцов (можно настроить)
        table.setHorizontalHeaderLabels([
            "Дата", "Время начала", "Время окончания",
            "Тип тренировки", "Статус", "Имя клиента"
        ])  # Заголовки столбцов

        # Заполнение таблицы
        for row_idx, row_data in enumerate(info):
            table.setItem(row_idx, 0, QTableWidgetItem(row_data[8]))  # Дата
            table.setItem(row_idx, 1, QTableWidgetItem(row_data[9]))  # Время начала
            table.setItem(row_idx, 2, QTableWidgetItem(row_data[10]))  # Время окончания
            table.setItem(row_idx, 3, QTableWidgetItem(row_data[11]))  # Тип тренировки
            table.setItem(row_idx, 4, QTableWidgetItem(row_data[6]))  # Статус
            table.setItem(row_idx, 5, QTableWidgetItem(f"{row_data[13]} {row_data[14]}"))  # Имя клиента

        # Настройка таблицы
        table.resizeColumnsToContents()  # Подгоняем ширину столбцов
        table.resizeRowsToContents()  # Подгоняем высоту строк

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Запрет редактирования

        # Добавление таблицы в текущий макет
        self.layout.addWidget(table)

    # Метод для обработки двойного клика
    def handle_item_double_click(self, item):
        reservation_data = item.data(Qt.ItemDataRole.UserRole)  # Извлекаем данные тренировки
        self.show_reservation_dialog(reservation_data)

    # Метод для отображения диалогового окна
    def show_reservation_dialog(self, reservation_data):
        # Создаём диалоговое окно
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Убираем верхние кнопки
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)  # Блокируем основное окно
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f7f9fc;
                border: 2px solid #5b9bd5;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QPushButton {
                background-color: #5b9bd5;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #407ec9;
            }
            QPushButton:pressed {
                background-color: #2f65a0;
            }
        """)

        # Основной макет диалогового окна
        layout = QVBoxLayout(dialog)

        # Добавляем информацию о тренировке
        info_label = QLabel(f"""
            <b>Дата:</b> {reservation_data[8]}<br>
            <b>Время:</b> {reservation_data[9]} - {reservation_data[10]}<br>
            <b>Тип:</b> {reservation_data[11]}<br>
            <b>Тренер:</b> {reservation_data[13]} {reservation_data[14]}<br>
            <b>Текущий статус:</b> {reservation_data[6]}
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(info_label)

        # Пространство между информацией и кнопками
        layout.addStretch()

        # Кнопка "Закрыть"
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.reject)  # Закрывает диалоговое окно
        layout.addWidget(close_button)

        # Кнопка "Отменить запись"
        cancel_button = QPushButton("Отменить запись")
        cancel_button.clicked.connect(lambda: self.cancel_reservation(dialog, reservation_data))
        layout.addWidget(cancel_button)

        # Настройка кнопок
        close_button.setFixedWidth(150)
        cancel_button.setFixedWidth(150)
        close_button.setFixedHeight(40)
        cancel_button.setFixedHeight(40)

        # Центрируем кнопки
        button_layout = QVBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Устанавливаем макет и показываем диалог
        dialog.setLayout(layout)
        dialog.resize(400, 250)
        dialog.exec()

    # Метод для отмены записи
    def cancel_reservation(self, dialog, reservation_data):
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите отменить запись?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            # Здесь вызываем функцию для изменения статуса
            success = change_status("Отменена", self.user_login, reservation_data[4])
            if success:
                self.show_temporary_message("Запись успешно отменена!", duration=3000)
                self.load_active_reservations()
                dialog.accept()  # Закрываем диалог
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось отменить запись.")

    def open_trainers_window(self):
        # Очистка текущих виджетов
        self.clear_layout(self.layout)

        trainer_info = check_trainers()
        if not trainer_info:
            QMessageBox.information(self, "Информация", "Список тренеров пуст.")
            return

        # Зона для отображения тренеров
        self.Tscroll_area.setWidget(self.trainers_widget)
        self.layout.addWidget(self.Tscroll_area)

        # Очистка макета тренеров
        for i in reversed(range(self.trainers_layout.count())):
            widget = self.trainers_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        max_columns = 3  # Максимальное количество виджетов в строке
        row = 0  # Текущая строка
        col = 0  # Текущий столбец

        for trainer_id, trainer_name, trainer_surname, specialization, username in trainer_info:
            trainer_widget = self.create_trainer_widget(
                trainer_id,
                f"{trainer_name} {trainer_surname}",
                specialization
            )
            self.trainers_layout.addWidget(trainer_widget, row, col, alignment=Qt.AlignmentFlag.AlignHCenter)

            # Логика для перехода на новую строку
            col += 1
            if col >= max_columns:
                col = 0  # Сброс столбца
                row += 1  # Переход на следующую строку

    def create_trainer_widget(self, trainer_id, trainer_name, specialization):
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.StyledPanel)
        widget.setStyleSheet(f"""
                    QFrame {{
                        background-color: "#ADD8E6";
                        border: 0px solid #000;
                        border-radius: 15px;
                        min-height: 80px;
                        max-height: 80px;
                        min-width: 300px;
                        max-width: 300px;
                    }}
                    QLabel {{
                        color: #000;
                        border-radius: 5px;
                        min-height: 30px;
                        max-height: 30px;
                        min-width: 90px;
                        max-width: 200px;
                        padding: 0px;
                        word-wrap: break-word;
                        text-align: center;
                        font-style: Arial Black;
                        font-size: 14px;  /* Увеличен размер шрифта */
                        font-weight: bold;
                    }}
                """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Время
        time_label = QLabel(trainer_name)
        time_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(time_label)

        # Название тренировки
        name_label = QLabel()
        name_label.setText(specialization)
        name_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(name_label)


        # Клик для открытия деталей
        widget.mousePressEvent = lambda _, id=trainer_id, n=trainer_name, s=specialization: \
            self.open_trainers_details(id, n, s)

        return widget

    def open_trainers_details(self, trainer_id, trainer_name, specialization):
        training_data = {
            "id": trainer_id,
            "name": trainer_name,
            "specialization": specialization
        }
        self.show_trainer_details(training_data, self)

    def show_trainer_details(self, training_data, parent=None):
        dialog = QDialog(parent)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Убираем верхние кнопки
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)  # Блокируем основное окно
        dialog.setStyleSheet("""
                QDialog {
                    background-color: #f7f9fc;
                    border: 2px solid #5b9bd5;
                    border-radius: 10px;
                }
                QLabel {
                    font-size: 14px;
                    color: #333333;
                }
                QPushButton {
                    background-color: #5b9bd5;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #407ec9;
                }
                QPushButton:pressed {
                    background-color: #2f65a0;
                }
            """)

        dialog.setWindowTitle("Детали тренировки")
        dialog.resize(400, 250)

        layout = QVBoxLayout(dialog)

        # Описание тренировки
        description_label = QLabel(f"""
            <b>Тренер:</b> {training_data['name']}<br>
            <b>Основной профиль:</b> {training_data['specialization']}<br>
            """)

        layout.addWidget(description_label)

        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.exec()

    def load_attendance_history(self):

        # Очистка текущих виджетов
        self.clear_layout(self.layout)

        # Получение данных о посещениях тренировок
        att_info = check_attendance(self.client_id)

        # Проверка наличия данных
        if not att_info:
            print("Нет записей для отображения.")
            return

        # Создание таблицы
        table = QTableWidget()
        table.setRowCount(len(att_info))  # Устанавливаем количество строк
        table.setColumnCount(5)  # Количество столбцов (можно настроить)
        table.setHorizontalHeaderLabels([
            "Дата", "Время начала", "Время окончания",
            "Тип тренировки", "Имя тренера"
        ])  # Заголовки столбцов

        # Заполнение таблицы
        for row_idx, row_data in enumerate(att_info):
            table.setItem(row_idx, 0, QTableWidgetItem(row_data[3]))  # Дата
            table.setItem(row_idx, 1, QTableWidgetItem(row_data[4]))  # Время начала
            table.setItem(row_idx, 2, QTableWidgetItem(row_data[5]))  # Время окончания
            table.setItem(row_idx, 3, QTableWidgetItem(row_data[6]))  # Тип тренировки
            table.setItem(row_idx, 4, QTableWidgetItem(f"{row_data[8]} {row_data[7]}"))  # Имя тренера

        # Настройка таблицы
        table.resizeColumnsToContents()  # Подгоняем ширину столбцов
        table.resizeRowsToContents()  # Подгоняем высоту строк

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Запрет редактирования

        # Добавление таблицы в текущий макет
        self.layout.addWidget(table)
