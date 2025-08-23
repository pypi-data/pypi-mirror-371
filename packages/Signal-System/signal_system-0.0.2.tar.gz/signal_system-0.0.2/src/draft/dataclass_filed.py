from dataclasses import dataclass, field, fields

from ss.utility.descriptor import DataclassDescriptor


class AgeDescriptor(DataclassDescriptor[int]):
    def __set__(
        self,
        obj: object,
        value: int,
    ) -> None:
        if value < 0:
            raise ValueError("Age must be greater than or equal to 0.")
        super().__set__(obj, value)


@dataclass
class Person:

    name: str
    age: AgeDescriptor = AgeDescriptor(None)
    email: str = "example@email.com"


# Get all fields
for field in fields(Person):
    default = (
        "No default"
        if field.default is field.default_factory
        else field.default
    )
    print(f"Field: {field.name}, Type: {field.type}, Default: {default}")

person = Person("John")
print(person.age)
person.age = -2
print(person.age)
