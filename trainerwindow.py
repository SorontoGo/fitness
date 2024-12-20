import sys
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QListWidget, QTableWidget, QTableWidgetItem, QCalendarWidget,
    QFormLayout, QLineEdit, QFileDialog, QMessageBox, QTextEdit, QListWidgetItem, QDialog
)
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QIcon
from PyQt6.QtCore import Qt, QRectF, QDate, QTime
from database import profile_info, check_reservation, check_trainers, change_status, client_search, insert_attendance
from ui.windows.basewindow import BaseWindow


class TrainerWindow(BaseWindow):
    def init_main_content(self):

        self.layout = self.main_content_layout

        trainer_info = check_trainers(self.user_login)
        for row in trainer_info:
            self.trainer_id = row[0]

        self.clear_layout(self.layout)

        # Список учеников
        self.reservation_list = QListWidget()
        self.reservation_list.setFixedSize(500, 50)

        # Редактор расписания
        self.schedule_view = QPushButton("Посмотреть расписание")
        self.schedule_view.setFixedSize(500, 35)
        self.layout.addStretch(1)
        self.schedule_view.clicked.connect(self.open_schedule)

        self.layout.addWidget(self.schedule_view)
        self.layout.addStretch(1)
        self.layout.addWidget(QLabel("Список записей:"))

        self.layout.addWidget(self.reservation_list)

        self.layout.addStretch(1)

        self.layout.setSpacing(10)  # Отступы между элементами
        self.layout.setContentsMargins(20, 20, 20, 20)  # Отступы от краев окна

        self.load_reservations()

    def load_reservations(self):

        self.reservation_list.clear()

        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        current_time = QTime.currentTime().toString("HH:mm")

        trainer_reservation = check_reservation(None, None, self.trainer_id)

        for reservation in trainer_reservation:
            status = reservation[6]
            day = reservation[8]
            startime = reservation[9]
            endtime = reservation[10]
            type = reservation[11]
            client_name = reservation[2]
            client_surname = reservation[3]

            is_past = day < current_date or (
                    day == current_date and startime < current_time
            )

            if status == "Активна":
                if is_past == True:
                    change_status("Неявка", self.user_login, reservation[4])
                else:
                    item_text = f"{day} {startime} - {endtime} {type} Спортсмен: {client_surname} {client_name}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, reservation)  # Сохраняем данные тренировки в элементе
                    self.reservation_list.addItem(item)

        self.reservation_list.itemDoubleClicked.connect(self.handle_double_click)

    def handle_double_click(self, item):
        reservation_data = item.data(Qt.ItemDataRole.UserRole)  # Извлекаем данные тренировки
        self.show_reservation_dialog(reservation_data)

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
                    <b>Имя спортсмена:</b> {reservation_data[2]} {reservation_data[3]}<br>
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
        cancel_button = QPushButton("Отметить посещение")
        cancel_button.clicked.connect(lambda: self.cancel_reservation(dialog, reservation_data, reservation_data[0]))
        layout.addWidget(cancel_button)

        # Настройка кнопок
        close_button.setFixedWidth(170)
        cancel_button.setFixedWidth(170)
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

    def cancel_reservation(self, dialog, reservation_data, user_id):

        client_username = client_search(user_id)
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите отменить посещение?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            # Здесь вызываем функцию для изменения статуса
            success = change_status("Завершена", client_username, reservation_data[4])
            if success:
                self.show_temporary_message("Отметка о посещении выставлена", duration=3000)
                insert_attendance(user_id, reservation_data[5])
                self.load_reservations()
                dialog.accept()  # Закрываем диалог
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось отменить запись.")
