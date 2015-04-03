__author__ = 'Owner'
import time
import thread


class HashTable:
    # creates an empty hash table (or 'dictionary')
    id = ""
    N = -1
    # constructor
    def __init__(self, id, N=-1):
        self.id = id
        self.hashTable = {}
        self.N = N

    def clean_once(self):
        while True:
            time.sleep(5)  # clear it self each 5s
            self.hashTable.clear()

    # For the server cache only
    def clean(self):
            thread.start_new_thread(self.clean_once, ())

    def get(self, key):
        # return self.hashTable[key]
        return self.hashTable.get(key)

    def put(self, key, value):
        # self.hashTable[key.strip()] = value
        self.hashTable[key] = value

    def _print(self):
        print "     ##############"
        print "     " + self.id + "[Key]: Value"
        print "     ##############"
        if len(self.hashTable.items()) == 0:
            print"     Empty " + self.id
        else:
            count = 1
            for key in sorted(self.hashTable):
                if self.id == "ServerCache":
                    print "     " + str(count) + "- " + self.id + "[" + str(key) + "]:" + self.hashTable[key].msg
                elif self.id == "KV":
                    print "     " + str(count) + "- " + self.id + "[" + str(key) + "/" + str(hash(key) % self.N) + "]:" + str(self.hashTable[key])
                else:
                    print "     " + str(count) + "- " + self.id + "[" + str(key) + "]:" + str(self.hashTable[key])
                count += 1
        print "     "

    def remove(self, key):
        try:
            val = "does no exist"
            if self.hashTable.get(key):
                val = self.hashTable[key]
                del self.hashTable[key]
            return val
        except:
            raise

    # for the aliveness table only
    def get_list_of_alive_keys(self):
        list_ = []
        for k in self.hashTable:
            if int(self.hashTable.get(k)) >= 0:
                list_.append(k + ":" + str(self.hashTable[k]))
        return list_


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
