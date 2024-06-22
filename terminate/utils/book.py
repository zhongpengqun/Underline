class Book:
    def __init__(self, book_path):
        self.book_path = book_path
        self.lines = self.to_lines()

    def to_lines(self):
        with open(self.book_path, 'r') as f:
            lines = f.readlines()
            print('--------------')
            for i, line in enumerate(lines):
                print(i)
                print(line)
            return lines

    @property
    def pages(self):
        pass
