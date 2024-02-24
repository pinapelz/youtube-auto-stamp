import os
class DataWriter:
    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(self.filepath, "w") as f:
            f.write("")
    
    def write(self, data: str):
        with open(self.filepath, "a") as f:
            f.write(data)