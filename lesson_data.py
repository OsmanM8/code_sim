# lessons_data.py
LESSONS = {
    "lesson1": {
        "title": "Intro to Integers",
        "description": "Declare an int variable 'age' with value 16 and print it.",
        "tasks": [
            {
                "var": "age",
                "type": "int",
                "value": 16,
                "must_print": True
            }
        ]
    },
    "lesson2": {
        "title": "Intro to Strings",
        "description": "Declare a string variable 'name' with value 'Alex' and print it.",
        "tasks": [
            {
                "var": "name",
                "type": "string",
                "value": "Alex",
                "must_print": True
            }
        ]
    },
    "lesson3": {
        "title": "Lesson 3: If Statements",
        "tasks": [
            {
                "vars": ["x"],
                "types": ["int"],
                "init_values": {"x": 5},
                "condition": "x > 3",
                "true_output": "Greater",
                "false_output": "Smaller",
                "must_print": True,
                "dynamic": True
            }
        ]
    },

    # -----------------------------
    # LESSON 4: LOOPS
    # -----------------------------
    "lesson4": {
        "title": "Lesson 4: Loops",
        "tasks": [
            {
                "vars": ["limit", "i"],
                "types": ["int", "int"],
                "init_values": {"limit": 3, "i": 0},
                "condition": "i < limit",
                "update": "i = i + 1",
                "cout_template": "iteration ",
                "must_print": True,
                "dynamic": True
            }
        ]
    },


    # -----------------------------
    # LESSON 5: CUMULATIVE
    # (Variables + arithmetic + if + loops)
    # -----------------------------
    "lesson5": {
        "title": "Lesson 5: Combined Logic, Arithmetic, Loops",
        "tasks": [
            {
                "vars": ["limit", "i", "value"],
                "types": ["int", "int", "int"],
                "init_values": {"limit": 4, "i": 0, "value": 10},

                "condition": "i < limit",

                "update": [
                    "i = i + 1",
                    "value = value * 2"         # arithmetic addition
                ],

                "cout_template": "Loop i=",  

                "expected_output": "dynamic",  
                "must_print": True,
                "dynamic": True
            }
        ]
    }
}
