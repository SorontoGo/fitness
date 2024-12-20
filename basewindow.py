from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, QWidget, QStackedWidget, QMessageBox,
    QTableWidget, QTableWidgetItem, QSplitter, QTextEdit, QLabel, QSizePolicy, QFrame, QDialog,
    QFileDialog, QGridLayout, QScrollArea, QSpacerItem
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QDate, QTime, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QIcon
from database import profile_info, schedule, training_reservation, check_reservation


class BaseWindow(QWidget):
    def __init__(self, window, user_login, role):
        super().__init__()
        self.window = window
        self.user_login = user_login
        self.role = role

        self.init_ui()

    def init_ui(self):
        # Основной макет окна
        self.main_layout = QVBoxLayout(self)

        # QSplitter для боковой панели и основного контента
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Боковая панель
        self.sidebar = self.create_sidebar()

        # Страница профиля
        self.profile_page = self.create_profile_page()

        # Основной контент
        self.main_content = QWidget()
        self.main_content_layout = QVBoxLayout(self.main_content)
        self.main_content.setLayout(self.main_content_layout)

        # Добавляем виджеты в QSplitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.main_content)
        self.splitter.setSizes([0, self.width()])  # Панель изначально скрыта

        # Верхняя панель с аватаром
        self.top_bar = self.create_top_bar()

        # Добавляем элементы в основной макет
        self.main_layout.addLayout(self.top_bar)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.splitter)

        # Инициализация основного контента
        self.init_main_content()

    def create_sidebar(self):
        sidebar = QWidget(self)
        sidebar.setStyleSheet("background-color: #2a3e8b; color: white;"
                              "border-radius: 3px;")
        layout = QVBoxLayout(sidebar)

        # Кнопка закрытия панели
        close_button = QPushButton("\u2630")
        close_button.setFixedSize(35, 35)
        close_button.setStyleSheet("background-color: transparent; color: white;")
        close_button.clicked.connect(self.toggle_sidebar)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignTop)

        # Кнопки на боковой панели
        buttons = [
            ("Главная", self.go_to_main_screen),
            ("Выйти из аккаунта", self.log_out)
        ]

        for text, callback in buttons:
            button = QPushButton(text)
            button.setStyleSheet(self.get_button_style())
            button.clicked.connect(callback)
            layout.addWidget(button)
            if text in "Главная":
                layout.addStretch()

        #layout.addStretch()
        return sidebar
    
    def go_to_main_screen(self):
        self.init_main_content()
        
    def create_top_bar(self):
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Кнопка открытия боковой панели
        self.toggle_button = QPushButton("\u2630")
        self.toggle_button.setObjectName("ToggleButton")
        self.toggle_button.setFixedSize(35, 35)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        top_bar.addWidget(self.toggle_button)

        # Кнопка аватара
        self.avatar_button = QPushButton()
        self.avatar_button.setObjectName("AvatarButton")
        self.avatar_button.setFixedSize(50, 50)
        self.avatar_button.setIcon(self.create_default_avatar_icon())
        self.avatar_button.setIconSize(self.avatar_button.size())
        self.avatar_button.setStyleSheet("border: none;"
                                         "background-color: none;")
        self.avatar_button.clicked.connect(lambda: self.window.stacked_widget.setCurrentWidget(self.profile_page))
        top_bar.addWidget(self.avatar_button)

        return top_bar

    def create_profile_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        page.setLayout(layout)

        try:
            ProfileInfo = profile_info(self.user_login, self.role)
            if not ProfileInfo:
                raise ValueError("Нет данных профиля.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки профиля: {e}")
            ProfileInfo = [["Неизвестно", "Неизвестно", "Неизвестно"]]

        # Верхняя часть с аватаркой
        avatar_layout = QVBoxLayout()
        avatar_label = QLabel()
        avatar_pixmap = QPixmap("defaultavatar.png")  # Укажите путь к изображению
        avatar_pixmap = avatar_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
        avatar_label.setPixmap(avatar_pixmap)
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(avatar_label)

        change_photo_button = QPushButton("Изменить фото")
        change_photo_button.setFixedSize(300, 50)
        change_photo_button.clicked.connect(self.change_avatar)
        avatar_layout.addWidget(change_photo_button)

        layout.addLayout(avatar_layout)

        # Нижняя часть с информацией о пользователе
        profile_layout = QFormLayout()

        Lusername = QLabel(self.user_login)
        Lname = QLabel(ProfileInfo[0][0])
        Lsurname = QLabel(ProfileInfo[0][1])
        Lbirthdate = QLabel(ProfileInfo[0][2])

        back_button = QPushButton("Назад")
        back_button.clicked.connect(lambda: self.window.stacked_widget.setCurrentWidget(self))
        back_button.setFixedSize(300, 50)

        log_out_button = QPushButton("Выйти из аккаунта")
        log_out_button.clicked.connect(self.log_out)
        log_out_button.setFixedSize(300, 50)

        profile_layout.addRow("Username:", Lusername)
        profile_layout.addRow("Имя:", Lname)
        profile_layout.addRow("Фамилия:", Lsurname)
        profile_layout.addRow("Email:", Lbirthdate)
        profile_layout.addWidget(back_button)
        profile_layout.addWidget(log_out_button)

        layout.addLayout(profile_layout)
        about_label = QLabel("Приложение: Система учёта спортивных тренировок\nВерсия: 1.0.0\nАвтор: Корчагин Павел")
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(about_label)

        self.window.stacked_widget.addWidget(page)
        return page

    def get_button_style(self):
        return """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 10px;
                text-align: center;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3c5a99;
            }
        """

    def create_default_avatar_icon(self):
        default_image_path = "defaultavatar.png"
        pixmap = QPixmap(default_image_path).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation)

        size = min(pixmap.width(), pixmap.height())
        circular_pixmap = QPixmap(size, size)
        circular_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(pixmap))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()

        return QIcon(circular_pixmap)

    def change_avatar(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать фото", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
                self.avatar_button.setIcon(self.create_circular_avatar_icon(pixmap))
            else:
                QMessageBox.warning(self, "Ошибка", "Невозможно загрузить изображение.")

    def create_circular_avatar_icon(self, pixmap):
        size = min(pixmap.width(), pixmap.height())
        result = QPixmap(size, size)
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawEllipse(0, 0, size, size)
        painter.setBrush(QBrush(pixmap))
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        return QIcon(result)

    def init_main_content(self):
        self.main_content_layout.addWidget(QLabel("Добро пожаловать!"))

    def toggle_sidebar(self):
        if self.sidebar.geometry().x() >= 0:  # Панель открыта
            self.splitter.setSizes([0, self.width()])
            self.toggle_button.show()  # Показываем кнопку открытия
        else:  # Панель скрыта
            self.splitter.setSizes([200, self.width() - 200])
            self.toggle_button.hide()  # Скрываем кнопку открытия

    def open_schedule(self):
        # Очистка текущей компоновки
        self.clear_layout(self.layout)
        # Панель с кнопками дней недели
        self.create_day_buttons_panel()

        # Зона для отображения тренировок
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.trainings_widget = QWidget()
        self.trainings_layout = QVBoxLayout(self.trainings_widget)
        self.scroll_area.setWidget(self.trainings_widget)
        self.layout.addWidget(self.scroll_area)

        # Загрузка расписания для текущей даты
        date = QDate.currentDate().toString("yyyy-MM-dd")
        self.load_schedule_for_day(date)

    def create_day_buttons_panel(self):
        # панель для кнопок дней недели
        self.days_layout = QHBoxLayout()
        self.layout.addLayout(self.days_layout)

        today = QDate.currentDate()
        for i in range(-2, 7):  # 2 дня до текущего и 6 после
            date = today.addDays(i)
            button = QPushButton(date.toString("ddd, dd MMM"))
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.clicked.connect(lambda _, d=date: self.load_schedule_for_day(d.toString("yyyy-MM-dd")))
            self.days_layout.addWidget(button)

            # Выделяем текущий день
            if i == 0:
                button.setChecked(True)

    def load_schedule_for_day(self, date):
        train_info = schedule(date)

        # Очистка текущих виджетов
        while self.trainings_layout.count():
            item = self.trainings_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Добавление верхнего промежутка
        self.trainings_layout.addSpacerItem(
            QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        # Проверка на наличие тренировок
        if not train_info:
            no_trainings_label = QLabel("Нет тренировок на выбранный день")
            no_trainings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.trainings_layout.addWidget(no_trainings_label)
            return

        # Сортировка по времени начала
        train_info.sort(key=lambda x: QTime.fromString(x[4], "HH:mm"))  # x[4] — это StartTime

        # Добавление тренировок
        current_date = QDate.currentDate()
        current_time = QTime.currentTime()
        selected_date = QDate.fromString(date, "yyyy-MM-dd")
        capacity_count = 0

        for trainer_name, trainer_surname, training_type, day, start_time, end_time, capacity, schedule_id in train_info:
            training_time = QTime.fromString(start_time, "HH:mm")

            reservations = check_reservation(None, schedule_id)

            for user_id, client_id, client_name, client_surname, reserv_id, scheduleID, reserv_status, trainID, Day, Start, End, Name, TrainerID, TrainerN, TrainerSN in reservations:
                if reserv_status == "Активна":
                    capacity_count += 1
            current_capacity = capacity - capacity_count

            is_past = selected_date < current_date or (
                    selected_date == current_date and training_time < current_time
            )

            is_sign_up_open = (
                                      not is_past
                                      and selected_date == current_date
                                      and current_time < training_time.addSecs(-30 * 60)
                              # Запись закрывается за 30 минут до начала
                              ) or (selected_date > current_date) and (capacity_count < capacity)


            training_widget = self.create_training_widget(
                f"{start_time} - {end_time}",
                training_type,
                f"{trainer_name} {trainer_surname}",
                f"Количество мест: {current_capacity} из {capacity}",
                abs(QTime.fromString(end_time, "HH:mm").secsTo(training_time) // 60),
                is_past,
                is_sign_up_open,
                schedule_id,
                current_capacity,
                capacity
            )
            self.trainings_layout.addWidget(training_widget, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Добавление нижнего промежутка
        self.trainings_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

    def create_training_widget(self, time, name, trainer, capacity_info, duration, is_past, is_sign_up_open, schedule_id, current_capacity, capacity):
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.StyledPanel)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {"#FFC0CB" if is_past else "#ADD8E6"};  /* Розовый для прошедших, синий для остальных */
                border: 0px solid #000;
                border-radius: 15px;
                min-height: 110px;
                max-height: 110px;
                min-width: 400px;
                max-width: 400px;
            }}
            QLabel {{
                color: #000;
                border-radius: 5px;
                min-height: 50px;
                max-height: 50px;
                min-width: 90px;
                max-width: 350px;
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
        time_label = QLabel(time)
        time_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(time_label)

        # Название тренировки
        name_label = QLabel()
        name_label.setText(f"""{name} - {trainer}
{capacity_info}"""
        )
        name_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(name_label)

        # Клик для открытия деталей
        widget.mousePressEvent = lambda _, t=time, n=name, tr=trainer, d=duration, s=is_sign_up_open, id=schedule_id: \
            self.open_training_details(t, n, tr, d, s, id)

        return widget

    def open_training_details(self, time, name, trainer, duration, is_sign_up_open, schedule_id):
        self.open_training_details_dialog({
            "time": time,
            "name": name,
            "trainer": trainer,
            "duration": duration,
            "is_sign_up_open": is_sign_up_open,
            "schedule_id": schedule_id
        }, self.user_login, self)

    def open_training_details_dialog(self, training_data, user_login, parent=None):
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
        <b>Тренировка:</b> {training_data['name']}<br>
        <b>Тренер:</b> {training_data['trainer']}<br>
        <b>Время:</b> {training_data['time']}<br>
        <b>Длительность:</b> {training_data['duration']} мин<br>
        """)
        layout.addWidget(description_label)

        schedule_id = training_data['schedule_id']

        # Кнопка записи (отображается только если запись открыта)
        if training_data.get("is_sign_up_open", False):
            sign_up_button = QPushButton("Записаться")
            layout.addWidget(sign_up_button)

            def sign_up():
                if training_reservation(user_login, schedule_id):  # Логика записи на тренировку
                    parent.show_temporary_message("Вы успешно записались на тренировку!")
                    self.open_schedule()
                    dialog.accept()

            sign_up_button.clicked.connect(sign_up)

        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.reject)
        layout.addWidget(close_button)

        dialog.exec()
        
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())  # Рекурсивно очистить вложенные layout

    def log_out(self):
        self.window.stacked_widget.setCurrentWidget(self.window.login_screen)

    def show_temporary_message(self, text, duration=3000):
        # Создаём и настраиваем QLabel
        message_label = QLabel(text, self)
        message_label.setStyleSheet("""
            QLabel {
                background-color: rgba(91, 155, 213, 0.8);
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.resize(300, 50)
        message_label.move((self.width() - message_label.width()) // 2, 50)
        message_label.show()

        # Таймер для плавного изменения прозрачности
        opacity = 0.0
        step = 0.05  # Шаг увеличения прозрачности

        def fade_in():
            nonlocal opacity
            opacity += step
            if opacity >= 0.9:
                opacity = 0.85
                QTimer.singleShot(duration, fade_out)  # Запускаем таймер на исчезновение
            else:
                message_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: rgba(91, 155, 213, {opacity});
                        color: white;
                        font-size: 14px;
                        border-radius: 10px;
                        padding: 10px;
                    }}
                """)
                QTimer.singleShot(50, fade_in)  # Рекурсивно вызываем функцию через небольшой интервал

        def fade_out():
            nonlocal opacity
            opacity -= step
            if opacity <= 0:
                message_label.deleteLater()
            else:
                message_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: rgba(91, 155, 213, {opacity});
                        color: white;
                        font-size: 14px;
                        border-radius: 10px;
                        padding: 10px;
                    }}
                """)
                QTimer.singleShot(50, fade_out)  # Рекурсивно вызываем функцию через небольшой интервал

        # Начинаем плавное увеличение прозрачности
        fade_in()
