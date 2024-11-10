import os
import abc
import requests
from selenium import webdriver

class Market_Interface():
    __metacalss__ = abc.ABCMeta

    __webdriver_name__ = "Chrome"
    __webdriver_file__ = "chromedriver.exe"

    __driver__ = None
    __session__ = None

    __market_name__ = ""

    def __init__(self, id, pw):
        self.id = id
        self.pw = pw

        self.__session__ = requests.session()

    def get_market_name(self):
        return self.__market_name__

    def set_market_name(self, market_name = str):
        self.__market_name__ = market_name

    def set_driver_file(self, path):
        self.__webdriver_file__ = path

    @abc.abstractmethod
    def login(self):
        pass

    @abc.abstractmethod
    def logout(self):
        pass

    def get_product_list(self):
        return list()

    @abc.abstractmethod
    def get_product_order_list(self):
        pass

    def get_webdriver(self):
        if(not os.path.isfile(self.__webdriver_file__)):
            print(self.__webdriver_file__ + " 파일이 존재하지 않습니다.")
            return None
        
        if(self.__driver__ == None):
            self.__driver__ = webdriver.Chrome(self.__webdriver_file__)

        return self.__driver__

    def close_webdriver(self):
        if (self.__driver__ != None):
            self.__driver__.close()
            self.__driver__ = None

    def __del__(self):
        self.close_webdriver()