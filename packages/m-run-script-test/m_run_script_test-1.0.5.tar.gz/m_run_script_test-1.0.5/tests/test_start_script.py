import time
from mobio.libs.run_script import start_script_cross_module


@start_script_cross_module(key='123455678')
def run():
    for i in range(2):
        time.sleep(3)
        print(i)


run()