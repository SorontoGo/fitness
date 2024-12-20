import sqlite3
from bcrypt import checkpw, hashpw, gensalt

def initialize_db():

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()
    cursor.execute("""
    """)
    connection.commit()
    connection.close()

def registration(username, password, email, first_name, last_name, middle_name, birthdate):

    userpassword = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    try:
        cursor.execute("""
                    INSERT INTO users (Role_ID, Username, UserPassword, Email)
                    VALUES (?, ?, ?, ?)
                """, (1, username, userpassword, email))
        last_id = cursor.lastrowid

        # Порядок столбцов в таблице clients: User_ID, Name, Surname, Patronymic, BirthDate
        cursor.execute("""
                    INSERT INTO clients (User_ID, Name, Surname, Patronymic, BirthDate)
                    VALUES (?, ?, ?, ?, ?)""", (last_id, first_name, last_name, middle_name, birthdate))
        connection.commit()

        return True


    except sqlite3.IntegrityError as e:

        print(f"IntegrityError: {e}")

        return False

    finally:
        connection.close()


def login_user(username, password):

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()
    cursor.execute("SELECT UserPassword FROM users WHERE Username = ?", (username,))
    user = cursor.fetchone()
    if user is None:
        return False

    connection.close()
    password_hash = user[0].encode('utf-8')

    if checkpw(password.encode('utf-8'), password_hash):
        return True
    return False

def check_role(username):

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()
    cursor.execute("SELECT Role_ID FROM users WHERE Username = ?", (username, ))
    roleID = str(cursor.fetchone())
    connection.close()

    return roleID

def profile_info(username, role):

    roleID = role
    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    # Получение информации о спортсмене
    if roleID == "1":
        cursor.execute("SELECT User_ID FROM users WHERE Username = ?", (username, ))
        value1 = cursor.fetchone()
        userID = value1[0]
        cursor.execute("SELECT Name, Surname, BirthDate FROM clients WHERE User_ID = ?", (userID, ))
        information = cursor.fetchall()

    # Получение информации о тренере
    elif roleID == "2":
        cursor.execute("SELECT User_ID FROM users WHERE Username = ?", (username,))
        value1 = cursor.fetchone()
        userID = value1[0]
        cursor.execute("SELECT Name, Surname, BirthDate FROM trainers WHERE User_ID = ?", (userID,))
        information = cursor.fetchall()

    # Получение информации об администраторе
    elif roleID == "3":
        cursor.execute("SELECT User_ID FROM users WHERE Username = ?", (username,))
        value1 = cursor.fetchone()
        userID = value1[0]
        cursor.execute("SELECT Name, Surname, BirthDate FROM admin WHERE User_ID = ?", (userID,))
        information = cursor.fetchall()

    return information

# Добавление тренировки в расписание (Админ)

def add_training(trainingID, trainerID, date, StartTraining, EndTraining, capacity):

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()
    try:
        cursor.execute("""
                    INSERT INTO train_schedule (Training_ID, Trainer_ID, Day, StartTime, EndTime, Capacity)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (trainingID, trainerID, date, StartTraining, EndTraining, capacity, ))
        connection.commit()

        return True

    except sqlite3.IntegrityError as e:

        print(f"IntegrityError: {e}")

        return False

    except sqlite3.Error as e:

        print(f"Database error: {e}")

        return False

    finally:
        connection.close()

def get_schedule_id(date, start_time, end_time):
    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT Schedule_ID 
            FROM train_schedule
            WHERE Day = ? AND StartTime = ? AND EndTime = ?
        """, (date, start_time, end_time))

        result = cursor.fetchone()
        print("result = ", result)
        return result[0] if result else None

    except sqlite3.DatabaseError as e:
        print(f"DatabaseError: {e}")
        return None
    finally:
        connection.close()

def delete_training(trainingID):
    print("Delete from DB...")
    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()
    try:
        cursor.execute("""
                DELETE FROM train_schedule WHERE Schedule_ID = ?
            """, (trainingID, ))

        connection.commit()  # Применяем изменения к базе данных
        return True

    except sqlite3.DatabaseError as e:
        print(f"DatabaseError: {e}")
        return False

    finally:
        connection.close()

def schedule(date):

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT 
        trainers.Name AS trainer_name,
        trainers.Surname AS trainer_surname,
        training_types.Name AS type,
        train_schedule.Day AS day,
        train_schedule.StartTime AS begin,
        train_schedule.EndTime AS end,
        train_schedule.capacity AS capacity,
        train_schedule.Schedule_ID AS schedule_id
    FROM
        train_schedule
    JOIN
        trainers ON train_schedule.Trainer_ID = trainers.Trainer_ID
    JOIN
        training_types ON train_schedule.Training_ID = training_types.Training_ID
    WHERE
        train_schedule.Day = ?;
    """, (date, ))

    train_info = cursor.fetchall()
    connection.close()
    return train_info

def training_reservation(username, schedule_id):
    
    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    cursor.execute("""
                SELECT clients.Client_ID 
                FROM users
                INNER JOIN clients ON users.User_ID = clients.User_ID
                WHERE users.Username = ?
            """, (username,))

    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Client with username '{username}' not found.")
    client_id = row[0]

    try:

        cursor.execute("""
        INSERT INTO reservations(Client_ID, Schedule_ID, ReservStatus) VALUES (?, ?, ?) 
        """, (client_id, schedule_id, "Активна", ))

        connection.commit()
        return True

    except sqlite3.IntegrityError as e:

        print(f"IntegrityError: {e}")

        return False

    except sqlite3.Error as e:

        print(f"Database error: {e}")

        return False

    finally:
        connection.close()

def check_reservation(username=None, schedule_id=None, trainer_id=None):
    # Подключение к базе данных
    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    # Базовый SQL-запрос
    query = """
        SELECT 
            users.User_ID,
            clients.Client_ID,
            clients.Name,
            clients.Surname,
            reservations.Reserv_ID,
            reservations.Schedule_ID,
            reservations.ReservStatus,
            train_schedule.Training_ID,
            train_schedule.Day,
            train_schedule.StartTime,
            train_schedule.EndTime,
            training_types.Name,
            train_schedule.Trainer_ID,            
            trainers.Name,
            trainers.Surname
        FROM 
            users
        INNER JOIN 
            clients ON users.User_ID = clients.User_ID
        INNER JOIN 
            reservations ON clients.Client_ID = reservations.Client_ID
        INNER JOIN 
            train_schedule ON reservations.Schedule_ID = train_schedule.Schedule_ID
        INNER JOIN
            training_types ON train_schedule.Training_ID = training_types.Training_ID
        INNER JOIN
            trainers ON train_schedule.Trainer_ID = trainers.Trainer_ID
    """

    # Условия фильтрации
    conditions = []
    parameters = []

    if username:
        conditions.append("users.Username = ?")
        parameters.append(username)

    if schedule_id:
        conditions.append("train_schedule.Schedule_ID = ?")
        parameters.append(schedule_id)

    if trainer_id:
        conditions.append("trainers.Trainer_ID = ?")
        parameters.append(trainer_id)

    # Добавляем условия в запрос, если они есть
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Выполняем запрос
    cursor.execute(query, tuple(parameters))

    # Получение и структурирование данных
    rows = cursor.fetchall()

    connection.close()

    return rows

def check_register_date():

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT DATE(Registration_Date) AS Registration_Date 
    FROM users
    """)

    info = cursor.fetchall()

    connection.close()

    return info
def check_reservation_status():

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT ReservStatus FROM reservations""")

    info = cursor.fetchall()

    connection.close()

    return info
def change_status(new_status, username, reservation_id):

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    try:
        cursor.execute("""
                    UPDATE reservations 
                    SET ReservStatus = ?
                    WHERE Client_ID = (
                        SELECT Client_ID FROM clients 
                        WHERE User_ID = (SELECT User_ID FROM users WHERE Username = ?)
                    ) AND Reserv_ID = ?
                    """, (new_status, username, reservation_id))

        connection.commit()

        if cursor.rowcount == 0:
            print("Ни одна запись не обновлена. Проверьте входные данные.")
            return False

        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

    finally:
        connection.close()

def check_trainers(username=None):
    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    query = """
        SELECT 
            trainers.Trainer_ID, 
            trainers.Name, 
            trainers.Surname, 
            trainers.Specialization,
            users.Username
        FROM trainers
        JOIN users ON trainers.User_ID = users.User_ID
        """

    # Условия фильтрации
    conditions = []
    parameters = []

    if username:
        conditions.append("users.Username = ?")
        parameters.append(username)

    # Добавляем условия в запрос, если они есть
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    try:
        # Выполнение запроса
        cursor.execute(query, parameters)
        trainers = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        trainers = []
    finally:
        connection.close()

    return trainers

def check_training_types():

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT Training_ID, Name FROM training_types""")

    types = cursor.fetchall()

    return types

def client_search(userID):

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT 
        users.Username 
    FROM clients
    JOIN users ON clients.User_ID = users.User_ID
    WHERE clients.User_ID = ?""", (userID, ))

    row = cursor.fetchone()
    info = row[0]
    connection.close()

    return info

def client_id_search(username):

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT User_ID FROM users WHERE username = ?""", (username, ))

    row = cursor.fetchone()
    info = row[0]
    connection.close()

    return info

def insert_attendance(client_ID, schedule_ID):

    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO attendance (Client_ID, Schedule_ID)
    VALUES (?, ?)""", (client_ID, schedule_ID, ))

    connection.commit()

    connection.close()

    return

def check_attendance(client_ID):
    connection = sqlite3.connect("gymDB.db")
    cursor = connection.cursor()
    
    cursor.execute("""
    SELECT 
        attendance.Schedule_ID,
        train_schedule.Training_ID,
        train_schedule.Trainer_ID,
        train_schedule.Day,
        train_schedule.StartTime,
        train_schedule.EndTime,
        training_types.Name,
        trainers.Name,
        trainers.Surname
    FROM attendance
    JOIN 
        train_schedule ON attendance.Schedule_ID = train_schedule.Schedule_ID
    JOIN 
        training_types ON train_schedule.Training_ID = training_types.Training_ID
    JOIN 
        trainers ON train_schedule.Trainer_ID = trainers.Trainer_ID
    WHERE attendance.Client_ID = ?
    """, (client_ID,))

    info = cursor.fetchall()
    print(info)
    return info