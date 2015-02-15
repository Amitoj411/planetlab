__author__ = 'Owner'


class Ring:
    __element1 = 123
    __element2 = "this is Africa"
    hashTable = {}   # creates an empty hash table (or 'dictionary')
    # can also say ID = dict(), which creats a dict() object, {} is shortcut.


    #constructor
    # def __init__(self,x,y):
    #     self.x = x
    #     self.y = y
    description = "Ring is the consistent hashing part of the algorithm"

    def get(self, key):
        return self.hashTable[key]

    def put(self, key, value):
        self.hashTable[key] = value

    def _print(self):
        for key, value in self.hashTable.items():
            print key, ":", value      # prints each key-value pair.

    def remove(self, key):
        try:
            self.hashTable.pop(key, None)
        except:
            raise

