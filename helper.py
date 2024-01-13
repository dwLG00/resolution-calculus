class RecursiveFlag:
    def __init__(self):
        self.value = False

    def toggle(self):
        self.value = True

    def reset(self):
        self.value = False

    def __bool__(self):
        return self.value
