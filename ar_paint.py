#!/usr/bin/python3

def main():

    # ............. Initialization ...........................

    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    args = vars(parser.parse_args())




if __name__ == '__main__':
    main()