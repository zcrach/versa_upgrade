from this import s


class Person:
    def __init__(self, age, weight, height, first_name, last_name, catch_phrase):
        self.age = age
        self.weight = weight
        self.height = height
        self.first_name = first_name
        self.last_name = last_name
        self.catch_phrase = catch_phrase

    def walk(self):
        print("Walking...")
    
    def run(self):
        print("Running...")


user = Person(25, 80, 177, "Jon", "snow", "You know nothing jon snow")

print(user.age)

user.walk()

class VersaAttributes:
    def __init__(self, serial_number, version):
        self.serial_number = serial_number
        self.version = version


device = VersaAttributes()