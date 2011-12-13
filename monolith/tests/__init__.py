import unittest


def main():
    print unittest.defaultTestLoader.discover('.')
    unittest.main()

if __name__ == '__main__':
    main()

