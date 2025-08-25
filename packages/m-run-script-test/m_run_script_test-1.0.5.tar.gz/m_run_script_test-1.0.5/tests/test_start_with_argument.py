import argparse
import time
from mobio.libs.run_script import start_script_cross_module


def run(key):
    @start_script_cross_module(key=key)
    def handle_logic():
        for i in range(2):
            time.sleep(3)
            print(i)

    handle_logic()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="", required=True, type=str)
    args = parser.parse_args()
    key = args.key

    run(key)
