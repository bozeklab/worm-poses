import configparser


class Settings:
    __conf = None

    @staticmethod
    def config():
        if Settings.__conf is None:
            Settings.__conf = configparser.ConfigParser()
            Settings.__conf.read('settings.ini')
        return Settings.__conf
