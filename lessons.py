from lesson_validators import (
    lesson_1_validator,
    lesson_2_validator,
    lesson_3_validator,
    lesson_4_validator,
    lesson_5_validator
)

lessons = [
    {
        "id": 1,
        "title": "Declare and Print an Integer",
        "instructions": "Declare an int variable called age = 16 and print it using cout.",
        "validator": lesson_1_validator
    },
    {
        "id": 2,
        "title": "Declare and Print a String",
        "instructions": "Declare string name = 'Alex' and print it using cout.",
        "validator": lesson_2_validator
    },
    {
        "id": 3,
        "title": "Combine Text and Variables",
        "instructions": "Print 'Hello' followed by the variable 'name'.",
        "validator": lesson_3_validator
    },
    {
        "id": 4,
        "title": "Arithmetic Practice",
        "instructions": "Declare two ints a = 3 and b = 5, create a sum variable equal to a + b, and print the sum.",
        "validator": lesson_4_validator
    },
    {
        "id": 5,
        "title": "Loop Practice (Capstone)",
        "instructions": "Use a for loop to print numbers 1 through 5.",
        "validator": lesson_5_validator
    }
]
