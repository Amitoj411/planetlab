__author__ = 'Owner'
import settings


# def init():
#     for i in range(0, int(settings.N)):
#         settings.vector_stamp_table[i] = 0


def advance_local_time_stamp():
    settings.vector_stamp_table[int(settings.hashedKeyModN)] += 1
    print "Advance local time stamp", settings.get_vector_stamp_string()


def incoming_vector_stamp(vector_stamp_string):
    vector_stamp_list = vector_stamp_string.split(',')
    for index in range(0, int(settings.N)):
        if index != int(settings.hashedKeyModN):
            if settings.vector_stamp_table[index] < int(vector_stamp_list[index]):
                settings.vector_stamp_table[index] = int(vector_stamp_list[index])
    else:
        advance_local_time_stamp()


def is_first_vector_less_than_the_second(first_vector_stamp_string, second_vector_stamp_string):
    all_less_than_or_equal = True
    first_vector_stamp = first_vector_stamp_string.split(',')
    second_vector_stamp = second_vector_stamp_string.split(',')
    for index in range(0, int(settings.N)):
        if int(first_vector_stamp[index] > int(second_vector_stamp[index])):
            all_less_than_or_equal = False

    if all_less_than_or_equal:
        for index in range(0, int(settings.N)):
            if int(first_vector_stamp[index] < int(second_vector_stamp[index])):
                print "Yes. first_vector_less_than_the_second"
                return True
        # an item less than is not found
        print "No1. first_vector_less_than_the_second"
        print first_vector_stamp_string, second_vector_stamp_string
        return False
    else:
        print "No2. first_vector_less_than_the_second"
        print first_vector_stamp_string, second_vector_stamp_string
        return False


