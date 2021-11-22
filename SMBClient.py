# Need to install pysmb packege.
# pysmb is an experimental SMB/CIFS library written in Python to support file sharing between Windows and Linux machines
from smb.SMBConnection import SMBConnection
import tempfile


class SMBClient:
    """SMB connection client."""

    user_name = ""
    password = ""
    ip = ""
    port = 445

    def __init__(self, user_name=user_name, password=password, ip=ip, port=port):
        """Инициализация данных при создании экземпляра класса.

        Args:
            user_name (str): имя пользователя для подключения к SMB серверу;
            password (str): пароль пользователя для подключения к SMB серверу;
            ip (str): IP адресс SMB сервера;
            port (int): порт для подключения к SMB серверу.
        """

        self.user_name = user_name
        self.password = password
        self.ip = ip
        self.port = port
        self.connection = None

    def __enter__(self):
        """Автоматически подключается к SMB серверу при использовании декоратора with.

        Returns:
            Экземпляр класса SMBClient.
        """

        print(f"\nПодключаюсь к серверу {self.ip}.")
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматически отклюючается от сервера при использовании декоратора with."""

        if self.connection:
            print(f"\nОтключаюсь от сервера {self.ip}")
            self.disconnect()

    def connect(self):
        """Выполняет подключения к SMB серверу.

        Returns:
            Экземпляр класса SMBConnection.
        """

        self.connection = SMBConnection(
            self.user_name, self.password, " ", " ", " ", is_direct_tcp=True
        )

        try:
            assert self.connection.connect(self.ip, self.port, timeout=15)
        except AssertionError:
            print(f"Подключение к серверу {self.ip} не удалось.")
            self.connection.close()
            self.connection = None
            return self.connection
        except Exception as e:
            print(f"ОШИБКА:{e}")
            self.connection.close()
            self.connection = None
            return self.connection
        else:
            print(f"Подключение к серверу {self.ip} выполнено успешно.\n")
            return self.connection

    def disconnect(self):
        """Прерывает подключение к SMB серверу."""

        if self.connection:
            self.connection.close()
            print(f"Подключение к серверу {self.ip} закрыто.\n")

    def list_folder(self, share_name, path):
        """Возвращает список файлов и папок по указанному пути.

        Args:
            share_name (str): имя расшареного ресурса на SMB сервере;
            path (str): путь к каталогу.

        Returns:
            список файлов и папок в указанном каталоге, если во время выполнения
            метода не возникло ошибок, иначе None.
        """

        files = []
        try:
            for item in self.connection.listPath(share_name, path):
                if item.filename == ".":
                    pass
                elif item.filename == "..":
                    pass
                else:
                    files.append(item.filename)
        except Exception as e:
            print(e.message)
            return None
        else:
            return files

    def retrive_file(self, share_name, file_path):
        """Получение файла с SMB сервера.

        Args:
            share_name (str): имя расшаренного ресурса на SMB сервере;
            file_path (str): путь к требуемому файлу;

        Returns:
            file object.
        """

        f = tempfile.TemporaryFile()
        try:
            self.connection.retrieveFile(share_name, file_path, f)
        except Exception as e:
            print("Ошибка получения файла:")
            print(e.message)
            return None
        else:
            f.seek(0)
            return f


if __name__ == "__main__":

    user_name = "nets"
    password = "nets"
    ip = "10.15.41.36"
    share_name = "temp"
    path = "/ГЩУ/"
    file_name = "Макет 10015.txt"
    file_path = path + file_name

    with SMBClient(user_name, password, ip) as smb_con:
        print(smb_con.list_folder(share_name, path))
        reader = smb_con.retrive_file(share_name, file_path)
        if reader:
            for line in reader:
                print(line)
            reader.close()
