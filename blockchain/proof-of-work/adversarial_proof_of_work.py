import os
import time
import string
import random
import hashlib
import threading

def pow(word = None, difficulty=1, verbose=False, adversarial = False):
    if word is None:
        word = random_word()
    count = 0
    if not adversarial:
        print("STARTING IN NON-ADVERSARIAL MODE ===>")
        hard_work(word, difficulty, verbose, count)
    if adversarial:
        print("STARTING IN ADVERSARIAL MODE ===>")
        t1 = threading.Thread(target=hard_work, args=(word, difficulty, verbose, count))
        t2 = threading.Thread(target=hard_work, args=(word, difficulty, verbose, count, 50, 50))
        t3 = threading.Thread(target=hard_work, args=(word, difficulty, verbose, count, 100, 100))
        t4 = threading.Thread(target=hard_work, args=(word, difficulty, verbose, count, 150, 150))
        t5 = threading.Thread(target=hard_work, args=(word, difficulty, verbose, count, 200, 200))
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()

def hard_work(word, difficulty, verbose, count, starting_point_x=0, starting_point_y=0):
    start = time.time()
    # Computing arbitrary hash function to find an hash with a specific
    # number of leading zero(s) (difficulty)
    while True:
            for y in range(starting_point_y, 256):
                for x in range(starting_point_x, 256):
                    h = hashlib.sha256((f"{word}{chr(x)}").encode('utf-8')).hexdigest()
                    count += 1
                    if verbose:
                        print(f"Try: {count} - {h}")
                    if h[0:difficulty] == ('0' * difficulty):
                        end = time.time()
                        print(f"\n ################### Work took {end-start} seconds ################### \n\n")
                        os._exit(1)
                word = f"{word}{chr(y)}"


def random_word():
    return ''.join([random.choice(string.ascii_letters) for n in range(20)])

if __name__ == "__main__":
    word="this_is_a_test_string"
    difficulty = 5
    pow(word, difficulty, verbose=False, adversarial=True)
