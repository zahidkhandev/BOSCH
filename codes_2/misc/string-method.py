class Person:

    def __init__(self, first_name, last_name, age):

        self.first_name = first_name

        self.last_name = last_name

        self.age = age

    def __str__(self):

        return f'Person({self.first_name},{self.last_name},{self.age})'    

person = Person('John', 'Doe', 25)

print(person)
 