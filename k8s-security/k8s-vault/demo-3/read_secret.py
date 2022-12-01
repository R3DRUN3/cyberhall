#!/usr/bin/env python3
import time as t

SECRET_PATH = '/vault/secrets/helloworld' # This is the path inside the container, you can also pass this as an env variable

while(True):
    try:
        with open(SECRET_PATH) as f:
            lines = f.readlines()
            print(f"THE SECRET IS: \n {lines}")
    except Exception as e:
        print(f"ERROR: {e}")
    t.sleep(10) # sleep ten seconds
