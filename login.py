from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QTableWidget, \
    QTableWidgetItem, QDialog, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import login_user, check_role
from ui.windows.clientwindow import ClientWindow

class LoginWidget(QDialog):
    def __init__(self, parent_window):
        super().__init__()
        self.parent = parent_window

        # Макет
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addStretch(1)
        # Поля ввода
        self.username_input = self.add_input_field("Имя пользователя:", layout)
        self.password_input = self.add_input_field("Пароль:", layout, password=True)

        # Кнопка авторизации
        login_button = QPushButton("Войти")
        login_button.setFixedSize(300, 50)
        login_button.setFont(QFont("Arial", 14))
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)
        layout.addStretch(1)
        # Кнопка назад
        back_button = QPushButton("Назад")
        back_button.setFont(QFont("Arial", 14))
        back_button.clicked.connect(self.parent.show_main_screen)
        layout.addWidget(back_button)
        
    def clear_fields(self):
        # Очищает поля ввода
        self.username_input.clear()
        self.password_input.clear()

    #Функция добавляет метку и поле ввода в указанный макет
    def add_input_field(self, label_text, layout, password=False):
        # Создание метки
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 12))
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Выравнивание метки
        layout.addWidget(label)

        # Создание поля ввода
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
        spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        return input_field

    def login(self):
        input_username = self.username_input.text()
        input_password = self.password_input.text()

        if login_user(input_username, input_password):
            info = check_role(input_username)
            roleID = info[1]
            
            if roleID == "1":
                self.parent.show_client_window(input_username, roleID)
            
            if roleID == "2":
                self.parent.show_trainer_window(input_username, roleID)
            
            if roleID == "3":
                self.parent.show_admin_window(input_username, roleID)
            # Очистка полей ввода (в случае выхода из аккаунта они будут пустыми)
            self.clear_fields()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")

    def resizeEvent(self, event):
        #Обновляет максимальную ширину поля ввода при изменении размеров окна.
        super().resizeEvent(event)
        max_width = self.width() // 3
        self.username_input.setMaximumWidth(max_width)
        self.password_input.setMaximumWidth(max_width)
