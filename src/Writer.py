import csv
from typing import Union
from src.Page import Page, GamePage


class Writer(object):

    def __init__(self, type):
        self.type = type
        self.__open_file()
        self.writer = csv.writer(self.file)
        self.writer.writerow(type.get_header())

    def __open_file(self):
        if self.type == GamePage:
            fname = 'games'
        else:
            assert False
        self.file = open(fname+'.csv', 'w', encoding='UTF8', newline='')

    def save(self, row):
        self.writer.writerow(row)





