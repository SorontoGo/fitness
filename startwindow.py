from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QStackedWidget, \
    QHBoxLayout, QApplication
from PyQt6.QtGui import QKeyEvent, QFont, QGuiApplication, QPixmap
from PyQt6.QtCore import Qt
from ui.registration import RegistrationWidget
from ui.login import LoginWidget
from ui.windows.clientwindow import ClientWindow
from ui.windows.trainerwindow import TrainerWindow
from ui.windows.adminwindow import AdminWindow

class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("KoR&ChaGa")
        # Настройка окна
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )

        # Создаем QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Инициализируем экраны
        self.main_screen = MainScreen(self)
        self.registration_screen = RegistrationWidget(self)
        self.login_screen = LoginWidget(self)

        # Добавляем экраны в QStackedWidget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.registration_screen)
        self.stacked_widget.addWidget(self.login_screen)

        # Устанавливаем начальный экран
        self.stacked_widget.setCurrentWidget(self.main_screen)

        # Устанавливаем размеры окна
        self.setGeometry(0, 0, 1200, 750)

        # Центрируем окно
        self.center_window()

    def center_window(self):
        # Получаем главный экран
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Получаем размеры окна
        window_geometry = self.geometry()

        # Вычисляем координаты для центра окна
        center_x = screen_geometry.width() / 2 - window_geometry.width() / 2
        center_y = screen_geometry.height() / 2 - window_geometry.height() / 2

        # Устанавливаем позицию окна по центру экрана
        self.move(center_x, center_y)

    def show_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)

    def show_registration_screen(self):
        self.stacked_widget.setCurrentWidget(self.registration_screen)

    def show_login_screen(self):
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def show_client_window(self, user_login, roleID):
        self.profile_window = ClientWindow(self, user_login, roleID)
        self.stacked_widget.addWidget(self.profile_window)
        self.stacked_widget.setCurrentWidget(self.profile_window)
        
    def show_trainer_window(self, user_login, roleID):
        self.profile_window = TrainerWindow(self, user_login, roleID)
        self.stacked_widget.addWidget(self.profile_window)
        self.stacked_widget.setCurrentWidget(self.profile_window)
        
    def show_admin_window(self, user_login, roleID):
        self.profile_window = AdminWindow(self, user_login, roleID)
        self.stacked_widget.addWidget(self.profile_window)
        self.stacked_widget.setCurrentWidget(self.profile_window)

    # Функция для обработки нажатия специальных клавиш
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F11:  # Нажатие клавиши "F11"
            self.toggle_fullscreen()  # Переключение окна в полноэкранный режим

        if event.key() == Qt.Key.Key_Escape:  # Нажатие клавиши "Esc"
            self.close()  # Закрыть окно

    # Функция для переключения между полноэкранным и оконным режимами
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showMaximized()  # Переключение в оконный полноэкранный режим
            self.is_fullscreen = False
        else:
            self.showFullScreen()  # Переключение в полноэкранный режим
            self.is_fullscreen = True


class MainScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        layout = QHBoxLayout()  # Используем горизонтальное размещение элементов
        self.setLayout(layout)

        # Левый раздел с информацией о приложении
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)  # Уменьшаем расстояние между элементами в левом разделе

        # Приветственное сообщение и советы
        title_label = QLabel("Добро пожаловать")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title_label)

        # Добавим совет дня
        daily_advice_label = QLabel("Совет дня: Начни день с чашки воды!")
        daily_advice_label.setFont(QFont("Arial", 14))
        daily_advice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(daily_advice_label)

        # Дополнительная информация о приложении
        info_label = QLabel("Приложение для тренировок и здоровья.")
        info_label.setFont(QFont("Arial", 12))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(info_label)

        # Картинка внизу
        image_label = QLabel(self)
        pixmap = QPixmap("startphoto.png")  # Указываем путь к изображению
        image_label.setPixmap(pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio))  # Масштабируем изображение
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(image_label)

        # Кнопки справа
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)  # Уменьшаем отступы между кнопками

        # Добавим пустое пространство сверху, чтобы кнопки выровнялись по центру
        right_layout.addStretch(1)  # Это выравнивает кнопки по вертикали в центре

        # Заголовок для правой части экрана
        action_title = QLabel("Войдите или создайте аккаунт")
        action_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        action_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(action_title)

        # Краткое описание
        description_label = QLabel("Получите доступ к персонализированным тренировкам и отслеживайте прогресс.")
        description_label.setFont(QFont("Arial", 12))
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(description_label)

        # Добавляем пустое пространство перед кнопками, чтобы они выровнялись по центру
        right_layout.addStretch(1)  # Это создает дополнительное пространство до кнопок

        # Кнопки для входа и регистрации (расположены по горизонтали)
        buttons_layout = QHBoxLayout()  # Используем горизонтальное расположение для кнопок

        register_button = QPushButton("Зарегистрироваться")
        register_button.setFont(QFont("Arial", 14))
        register_button.clicked.connect(self.parent.show_registration_screen)
        register_button.setFixedSize(200, 100)
        buttons_layout.addWidget(register_button)

        login_button = QPushButton("Войти")
        login_button.setFont(QFont("Arial", 14))
        login_button.clicked.connect(self.parent.show_login_screen)
        login_button.setFixedSize(200, 100)
        buttons_layout.addWidget(login_button)

        # Добавляем горизонтальные кнопки в основной правый layout
        right_layout.addLayout(buttons_layout)

        # Добавляем пустое пространство снизу, чтобы кнопки не прилипали к низу экрана
        right_layout.addStretch(1)

        # Добавляем два раздела в основной layout
        layout.addLayout(left_layout, stretch=1)  # Левый раздел
        layout.addLayout(right_layout)  # Правый раздел с кнопками
        # Запуск в оконном полноэкранном режиме
        self.show()
