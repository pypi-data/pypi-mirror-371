import logging
import sys

class DynamicLogger():
    def __init__(self, configs):
        self.__configs = configs
        logFormatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.rootLogger = logging.getLogger()
        self.rootLogger.setLevel(logging.INFO)

        if not self.rootLogger.handlers:
            fileHandler = logging.FileHandler(self.__configs["log_file"])
            fileHandler.setFormatter(logFormatter)
            self.rootLogger.addHandler(fileHandler)


    def __call__(self, logging_mode, message):
        self.rootLogger.log(logging_mode, message)