from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QDateEdit, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QDate, Qt
from database import registration
from ui.windows.clientwindow import ClientWindow
from ui.login import LoginWidget


class RegistrationWidget(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent = parent_window

        # Макет
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Поля ввода
        self.username_input = self.add_input_field("Имя пользователя:", layout)
        self.password_input = self.add_input_field("Пароль:", layout, password=True)
        self.email_input = self.add_input_field("Электронная почта:", layout)
        self.first_name_input = self.add_input_field("Имя:", layout)
        self.last_name_input = self.add_input_field("Фамилия:", layout)
        self.middle_name_input = self.add_input_field("Отчество (необязательно):", layout)

        # Поле для выбора даты рождения
        birth_date_label = QLabel("Дата рождения:")
        birth_date_label.setFont(QFont("Arial", 12))
        layout.addWidget(birth_date_label)

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setFixedSize(200, 30)
        self.birth_date_input.setFont(QFont("Arial", 12))
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate())
        layout.addWidget(self.birth_date_input)

        # Кнопка регистрации
        register_button = QPushButton("Зарегистрироваться")
        register_button.setFixedSize(300, 50)
        register_button.setFont(QFont("Arial", 14))
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        # Кнопка назад
        back_button = QPushButton("Назад")
        back_button.setFont(QFont("Arial", 14))
        back_button.clicked.connect(self.parent.show_main_screen)
        layout.addWidget(back_button)

    def add_input_field(self, label_text, layout, password=False):
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 12))
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setFont(QFont("Arial", 12))

        # Настройка режима отображения (скрытый ввод для пароля)
        if password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)

        # Установка размеров поля ввода
        input_field.setMinimumWidth(200)  # Минимальная ширина
        input_field.setMaximumWidth(self.width() // 3)  # Максимальная ширина — 1/3 окна
        input_field.setMinimumHeight(30)  # Минимальная высота

        layout.addWidget(input_field)
        # Добавляем разделитель между элементами
        spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        return input_field

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        middle_name = self.middle_name_input.text()
        check_birth_date = self.birth_date_input.date()
        birth_date = self.birth_date_input.date().toString("yyyy-MM-dd")

        today = QDate.currentDate()

        # Вычисление возраста
        age = today.year() - check_birth_date.year()

        # Корректировка возраста в зависимости от текущей даты и даты рождения
        if today < check_birth_date.addYears(age):  # Если текущий месяц/день еще не наступил после дня рождения
            age -= 1

        if not username or not password or not email or not first_name or not last_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return
        if len(str(username)) < 8:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя не может быть менее 8 символов")
            return
            # Проверка возраста
        min_age = 18
        if age < min_age:
            QMessageBox.warning(self, "Ошибка", "Вам должно быть не менее 18 лет.")
            return

       # Если отчество не было заполнено, передаём пробел
        if middle_name == None:
            middle_name = " "
        if registration(username, password, email, first_name, last_name, middle_name, birth_date) == True:
            QMessageBox.information(self, "Успех", f"Пользователь {username} успешно зарегистрирован!")
            self.parent.show_login_screen()
            
        else:
            QMessageBox.information(self, "Ошибка", "Логин занят")
