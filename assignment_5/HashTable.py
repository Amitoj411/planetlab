__author__ = 'Owner'
import time
import thread
import settings
import HeartBeat

class HashTable:
    # creates an empty hash table (or 'dictionary')
    id = ""
    # N = -1
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
                elif self.id == "AliveNess":
                    print "     " + str(count) + "- " + self.id + "[" + str(key) + "]:" + str(self.isAlivePrint(key))
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
        # print self.hashTable
        if len(self.hashTable) > 0:
            for k, v in self.hashTable.iteritems():
                # print "v", v
                list_.append(k + ":" + str(v.heart_beat_counter + 1))


            list_ = ','.join(list_)
            return list_
        else:
            return ""


    def isAlivePrint(self, key):
        hb_obj = self.hashTable.get(key)
        t = hb_obj.time
        if time.time() - t < settings.TFails:
            return "1, " + str(time.time() - t) + ", " + str(hb_obj.heart_beat_counter)
        elif settings.TFails < time.time() - t < settings.TClean:
            return "0, " + str(time.time() - t) + ", " + str(hb_obj.heart_beat_counter)
        else:  # way more than TClean
            return "-1, " + str(time.time() - t) + ", " + str(hb_obj.heart_beat_counter)

    def isAlive(self, key):
        # print "key", key
        # print "hashtable", self.hashTable.iterkeys()

        hb_obj = self.hashTable.get(key)
        if hb_obj:
            t = hb_obj.time
            if time.time() - t < settings.TFails:
                return True
            elif settings.TFails < time.time() - t < settings.TClean:
                return False
            else:  # way more than TClean
                return False
        else:
            return False



    # def get_vector_stamp_string(self):
    #     list_ = self.hashTable.values()
    #     return ','.join([str(i) for i in list_])


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
