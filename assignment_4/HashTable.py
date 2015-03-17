__author__ = 'Owner'
import time
import thread


class HashTable:
      # creates an empty hash table (or 'dictionary')
    id = ""

    # constructor
    def __init__(self, id):
        self.id = id
        self.hashTable = {}
    #     self.x = x
    #     self.y = y

    def clean_once(self):
        while True:
            time.sleep(10) # clear it self each 10s
            # for k in self.hashTable:
            #     del self.hashTable[k]
            self.hashTable.clear()

    def clean(self):
            thread.start_new_thread(self.clean_once, ())

    def get(self, key):
        # return self.hashTable[key]
        return self.hashTable.get(key)

    def put(self, key, value):
        self.hashTable[key.strip()] = value

    def _print(self):
        print "     ##############"
        print("     {}[Key]: Value".format(self.id))
        print "     ##############"
        if len(self.hashTable.items()) == 0:
            print("     Empty {}".format(self.id))
        else:
            count = 1
            for key, value in self.hashTable.items():
                if self.id == "ServerCache":
                    print "     " + str(count) + "- " + self.id + "[" + str(key) + "]:" + value.msg
                else:
                    print "     " + str(count) + "- " + self.id + "[" + str(key) + "]:" + str(value)
                count += 1
        print "     "

    def remove(self, key):
        try:
            val = self.hashTable[key]
            del self.hashTable[key]
            return val
        except:
            raise

    # def size(self):
    #     sum = 0
    #
    #     # lock
    #     # TODO mutual exclusion is needed
    #     for k, v in self.hashTable.iteritems():
    #         sum = sum + len(v)
    #     # un-lock
    #
    #     return sum
