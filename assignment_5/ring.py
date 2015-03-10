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
        self.hashTable[key.strip()] = value

    def _print(self):
        print "     ##############"
        print "     KV[Key]: Value"
        print "     ##############"
        if len(self.hashTable.items()) == 0:
            print "     Empty hashtable"
        else:
            count = 1
            for key, value in self.hashTable.items():
                print "     " + str(count) + "- KV[" + key + "]:" + value      # prints each key-value pair.
                count += 1
        print "     "

    def remove(self, key):
        try:
            val = self.hashTable[key]
            del self.hashTable[key]
            return val
        except:
            raise

    def size(self):
        sum = 0

        # lock
        # TODO mutual exclusion is needed
        for k, v in self.hashTable.iteritems():
            sum = sum + len(v)
        # un-lock

        return sum
