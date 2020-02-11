import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("wsi")
    parser.add_argument("results_dir")
    parser.add_argument("save_to")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    pass


if __name__ == '__main__':
    command = "python showresultonwsi.py [wsi] [results_dir] [save_to]"
