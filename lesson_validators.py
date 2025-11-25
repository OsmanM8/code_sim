from Cpp_engine import evaluate_output, extract_vars, check_prints
from lesson_data import LESSONS
import re 



def lesson1_validator(code: str, result: dict):
    """
    Returns: (success: bool, feedback: str)
    """

    printed_output = result["raw_output"].strip()
    vars_dict = result["variables"]

    # Your lesson 1 expects:
    # int age = 16; cout << age;
    expected_var = "age"
    expected_type = "int"
    expected_value = "16"

    # 1. Variable existence
    if expected_var not in vars_dict:
        return False, "You must declare a variable named 'age'."

    # 2. Type check
    if vars_dict[expected_var]["type"] != expected_type:
        return False, "'age' must be an int (e.g. int age = 16;)."

    # 3. Value check
    if str(vars_dict[expected_var]["value"]) != expected_value:
        return False, f"Set 'age' equal to {expected_value} (e.g. int age = 16;)."

    # 4. Print check
    if expected_value not in printed_output:
        return False, "Make sure to print 'age' using cout."

    return True, "Well done!"
 

def lesson2_validator(code: str, result: dict):
    printed_output = result["raw_output"].strip()
    vars_dict = result["variables"]

    expected_var = "name"
    expected_type = "string"
    expected_value = "Alex"

    if expected_var not in vars_dict:
        return False, "You must declare a variable named 'name'."

    if vars_dict[expected_var]["type"] != expected_type:
        return False, "'name' must be a string (e.g. string name = \"Alex\";)."

    if str(vars_dict[expected_var]["value"]) != expected_value:
        return False, f"Set '{expected_var}' equal to {expected_value} (e.g. string name = \"Alex\";)."

    if expected_value not in printed_output:
        return False, "Make sure to print 'name' using cout."

    return True, "Well done!"


# ===== Lesson 3 Validator =====
def lesson3_validator(code: str, result: dict):
    printed_output = result["output"].strip()
    vars_dict = result["variables"]

    task = LESSONS["lesson3"]["tasks"][0]

    var = task["vars"][0]
    expected_type = task["types"][0]
    init_value = task["init_values"][var]

    # Must declare variable
    if var not in vars_dict:
        return False, f"You must declare variable '{var}'."

    # Must match type
    if vars_dict[var]["type"] != expected_type:
        return False, f"'{var}' must be type {expected_type}."

    # Condition evaluation
    scope = {var: vars_dict[var]["value"]}

    try:
        cond_result = eval(task["condition"], {}, scope)
    except:
        return False, "Invalid if-statement condition."

    expected_output = task["true_output"] if cond_result else task["false_output"]

    if expected_output not in printed_output:
        return False, f"Expected printed output: '{expected_output}'."

    return True, "Correct if/else logic!"


# -------------------
# LESSON 4 — LOOPS
# -------------------
def lesson4_validator(code: str, result: dict):
    from lesson_data import LESSONS
    task = LESSONS["lesson4"]["tasks"][0]

    vars_dict = result["variables"]

    # ---- 1. Extract student cout output directly ----
    # IMPORTANT: use raw cout output, not simulation
    student_output_lines = result["output"].split("\n")
    student_output_clean = "".join(student_output_lines).replace(" ", "").strip()

    # ---- 2. Simulate the expected loop based on init + condition + update ----
    scope = dict(task["init_values"])
    expected_output = ""

    iterations = 0
    while eval(task["condition"], {}, scope):
        iterations += 1
        if iterations > 1000:
            return False, "Infinite loop detected."

        expected_output += f"{task['cout_template']}{scope['i']}"

        # apply update
        updates = task["update"]
        if not isinstance(updates, list):
            updates = [updates]

        for upd in updates:
            exec(upd, {}, scope)

    expected_clean = expected_output.replace(" ", "")

    # ---- 3. Compare actual to expected ----
    if student_output_clean == "":
        return False, "You must print loop output using cout."

    if student_output_clean != expected_clean:
        return False, (
            f"Expected: '{expected_output}' but got '{result['output']}'."
        )

    return True, "Loop logic is correct!"



# -------------------
# LESSON 5 — Combined logic
# -------------------

def lesson5_validator(code: str, result: dict):
    output_raw = result["output"]
    vars_dict = result["variables"]

    # ---- 1. Required variables ---------------------
    required_vars = ["limit", "i", "value"]
    for v in required_vars:
        if v not in vars_dict:
            return False, f"You must declare variable '{v}'."

        if vars_dict[v]["type"] != "int":
            return False, f"'{v}' must be an int."

    # ---- 2. Conditional test -----------------------
    limit_value = vars_dict["limit"]["value"]
    expected_cond_output = "Odd" if (limit_value % 2 == 1) else "Even"

    if expected_cond_output not in output_raw:
        return False, f"Your code must print '{expected_cond_output}' based on limit % 2."

    # ---- 3. Generate expected dynamic loop output ---
    task = LESSONS["lesson5"]["tasks"][0]
    expected_loop_output = []
    scope = dict(task["init_values"])

    while eval(task["condition"], {}, scope):
        expected_loop_output.append(f"loop: {scope['value']}")
        updates = task["update"]
        if not isinstance(updates, list):
            updates = [updates]
        for upd in updates:
            exec(upd, {}, scope)

    # ---- 4. Extract loop outputs ANYWHERE in output ----
    loop_lines = re.findall(r'loop:\s*\d+', output_raw)

    if not loop_lines:
        return False, "You must print loop output using cout."

    # ---- 5. Compare exact sequence -----------------------
    if loop_lines != expected_loop_output:
        return False, (
            "Loop output does not match.\n"
            f"Expected: {expected_loop_output}\n"
            f"Got: {loop_lines}"
        )

    return True, "Great job! Your conditional and loop logic are correct."




