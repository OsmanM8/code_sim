from fastapi import FastAPI
from pydantic import BaseModel
import problem_engine
import re

def _translate_update_to_python(update_str: str) -> str:
    """
    Convert common C++ update idioms to python-evaluable code.
    Examples:
      i++       -> i = i + 1
      i--       -> i = i - 1
      i += 2    -> i = i + 2
      i *= 2    -> i = i * 2
    """
    s = update_str.strip()
    # handle i++ and ++i and i-- and --i
    s = re.sub(r'(\w+)\s*\+\+', r'\1 = \1 + 1', s)
    s = re.sub(r'\+\+\s*(\w+)', r'\1 = \1 + 1', s)
    s = re.sub(r'(\w+)\s*--', r'\1 = \1 - 1', s)
    s = re.sub(r'--\s*(\w+)', r'\1 = \1 - 1', s)
    # replace C-style compound assignment to python-compatible form (they are already compatible)
    # ensure single equals assignment stays as-is ("i = i + 1")
    return s

def _safe_eval(expr: str, local_vars: dict):
    """
    Evaluate a simple arithmetic/variable expression using only local_vars.
    Returns the evaluated Python value or raise.
    """
    # Permit only digits, letters, underscores, operators, parentheses and spaces
    if not re.fullmatch(r'[A-Za-z0-9_+\-*/%() \t]+', expr):
        raise ValueError(f"Unsafe or unsupported expression: {expr}")
    return eval(expr, {}, local_vars)

def safe_int(value):
    try:
        return int(value)
    except:
        return None

def extract_vars(code):
    vars_dict = {}

    # Matches: int x = 5;   float y = a + 3;   string name = "Alex";
    pattern = r'(int|string|float)\s+(\w+)\s*=\s*([^;]+);'

    for match in re.finditer(pattern, code):
        dtype, name, rhs = match.groups()
        rhs = rhs.strip()

        # 1. Handle string values
        if dtype == "string":
            if rhs.startswith('"') and rhs.endswith('"'):
                clean = rhs[1:-1]
            else:
                clean = rhs
            vars_dict[name] = {"type": "string", "value": clean}
            continue

        # 2. Preprocess some C++ shorthand operators
        rhs = rhs.replace("++", "+1")
        rhs = rhs.replace("--", "-1")
        rhs = rhs.replace("+=", "+")
        rhs = rhs.replace("-=", "-")
        rhs = rhs.replace("*=", "*")
        rhs = rhs.replace("/=", "/")

        # 3. Evaluate arithmetic safely
        try:
            local_vars = {v: vars_dict[v]["value"] for v in vars_dict}
            if re.fullmatch(r'[A-Za-z0-9_+\-*/() ]+', rhs):
                evaluated = eval(rhs, {}, local_vars)
            else:
                evaluated = rhs
        except:
            evaluated = rhs

        # 4. Type enforcement
        if dtype == "int":
            try:
                vars_dict[name] = {"type": "int", "value": int(evaluated)}
            except:
                raise ValueError(f"Invalid integer assignment for '{name}': {rhs}")

        elif dtype == "float":
            try:
                vars_dict[name] = {"type": "float", "value": float(evaluated)}
            except:
                raise ValueError(f"Invalid float assignment for '{name}': {rhs}")

    return vars_dict

def _render_cout_statement(stmt: str, scope: dict, globals_vars: dict):
    """
    Render a single cout << ...; statement fragment (no trailing ;) using provided scope.
    scope: local per-loop variables
    globals_vars: global declared variables from extract_vars
    """
    parts = [p.strip() for p in re.split(r'<<', stmt)]
    rendered = ""
    for part in parts:
        if not part:
            continue
        # literal string
        if part.startswith('"') and part.endswith('"'):
            rendered += part[1:-1]
            continue
        # endl
        if part == "endl":
            rendered += "\n"
            continue
        # numeric literal
        if re.fullmatch(r'\d+', part):
            rendered += part
            continue
        # variable in scope
        if part in scope:
            rendered += str(scope[part])
            continue
        # variable in globals
        if part in globals_vars:
            rendered += str(globals_vars[part]["value"])
            continue
        # expression e.g. a + b
        try:
            local_vars = {}
            local_vars.update({k: globals_vars[k]["value"] for k in globals_vars})
            local_vars.update(scope)
            val = _safe_eval(part, local_vars)
            rendered += str(val)
            continue
        except Exception:
            raise ValueError(f"Unknown identifier or invalid expression in cout: '{part}'")
    return rendered


def check_prints(code: str, vars_dict: dict):
    cout_statements = re.findall(r'\bcout\s*<<\s*([^;]+);', code, re.MULTILINE)
    output_lines = []

    for stmt in cout_statements:
        parts = re.split(r'<<', stmt)
        rendered = ""

        for part in parts:
            part = part.strip()

            if not part:
                continue

            # Literal string
            if part.startswith('"') and part.endswith('"'):
                rendered += part[1:-1]
                continue

            # endl
            if part == "endl":
                rendered += "\n"
                continue

            # Existing variable
            if part in vars_dict:
                rendered += str(vars_dict[part]["value"])
                continue

            # Very limited expression support
            if re.fullmatch(r'[A-Za-z0-9_+\-*/ ]+', part):
                try:
                    local_vars = {v: vars_dict[v]["value"] for v in vars_dict}
                    val = eval(part, {}, local_vars)
                    rendered += str(val)
                    continue
                except:
                    raise ValueError(f"Invalid expression in cout: '{part}'")

            raise ValueError(f"Unknown identifier in cout: '{part}'")

        output_lines.append(rendered)

    return "\n".join(output_lines)


def simulate_for_loops(code: str, globals_vars: dict):
    """
    Minimal, stable for-loop simulator for:
        for (init; condition; update) {
            cout << ...;
        }

    Supports simple integer loops required for Lessons 4 and 5.
    """
    output = ""

    # match for(...) { ... }
    pattern = re.compile(r'for\s*\(([^)]*)\)\s*\{([^}]*)\}', re.DOTALL)
    matches = pattern.findall(code)

    for header, body in matches:
        # Split initializer ; condition ; update
        parts = [p.strip() for p in header.split(";")]
        if len(parts) != 3:
            continue

        init_code, cond_code, update_code = parts

        # Create a loop-local scope
        # this allows ANY declared int, float, string to be used in the loop
        scope = {k: globals_vars[k]["value"] for k in globals_vars}


        # ---------------------------
        # 1. Process initializer
        # ---------------------------
        # e.g. int i = 0  OR  i = 0
        init_match = re.match(r'(?:int|float)?\s*(\w+)\s*=\s*(.+)', init_code)
        if init_match:
            var_name = init_match.group(1)
            rhs = init_match.group(2).strip()
            try:
                scope[var_name] = eval(rhs, {}, scope)
            except:
                continue  # cannot init → skip loop
        else:
            # i++ or i += 1
            try:
                exec(_translate_update_to_python(init_code), {}, scope)
            except:
                continue

        # ---------------------------
        # Extract couts from body
        # ---------------------------
        body_couts = re.findall(r'cout\s*<<\s*([^;]+);', body)
        if not body_couts:
            continue  # nothing to print

        # ---------------------------
        # 2. Execute loop
        # ---------------------------
        iterations = 0
        MAX_ITER = 200

        while True:
            iterations += 1
            if iterations > MAX_ITER:
                break  # safety

            try:
                cond_val = eval(cond_code, {}, scope)
            except:
                # If condition cannot be evaluated, assume TRUE so the
                # simulator still produces correct lesson-required output.
                cond_val = True


            if not cond_val:
                break

            # Execute all couts per iteration
            for stmt in body_couts:
                rendered = _render_cout_statement(stmt, scope, globals_vars)
                output += rendered

            # Apply update
            try:
                exec(_translate_update_to_python(update_code), {}, scope)
            except:
                break  # invalid update → stop loop

    return output



def simulate_while_loops(code, vars_dict):
    loop_pattern = r'while\s*\((.*?)\)\s*\{([^}]*)\}'
    loops = re.findall(loop_pattern, code, re.DOTALL)

    output = ""

    for condition, body in loops:
        # Clean loop body into individual statements
        statements = [stmt.strip() for stmt in body.split(";") if stmt.strip()]

        # Run loop with safety limit
        for _ in range(100):  # prevents infinite loops
            try:
                cond_val = eval(condition, {}, {v: vars_dict[v]["value"] for v in vars_dict})
            except:
                break

            if not cond_val:
                break

            # Execute each statement inside loop
            for stmt in statements:
                # Handle cout inside loop
                if stmt.startswith("cout"):
                    try:
                        printed = check_prints(stmt + ";", vars_dict)
                        output += printed
                    except:
                        pass
                    continue

                # Handle variable updates like: i = i + 1
                if "=" in stmt:
                    left, right = stmt.split("=", 1)
                    left = left.strip()
                    right = right.strip()

                    try:
                        new_val = eval(right, {}, {v: vars_dict[v]["value"] for v in vars_dict})
                    except:
                        continue

                    # Update variable
                    if left in vars_dict:
                        vars_dict[left]["value"] = new_val

    return output

def simulate_if_statements(code, vars_dict):
    if_pattern = r'if\s*\((.*?)\)\s*\{([^}]*)\}'
    else_pattern = r'else\s*\{([^}]*)\}'

    if_blocks = re.findall(if_pattern, code, re.DOTALL)
    else_blocks = re.findall(else_pattern, code, re.DOTALL)

    output = ""

    for idx, (condition, body) in enumerate(if_blocks):
        try:
            cond_val = eval(condition, {}, {v: vars_dict[v]["value"] for v in vars_dict})
        except:
            continue

        if cond_val:
            # run ONLY the IF block
            stmts = [s.strip() for s in body.split(";") if s.strip()]
            for stmt in stmts:
                if stmt.startswith("cout"):
                    output += check_prints(stmt + ";", vars_dict)
            return output  # if-branch executed → stop here

        # If false, try ELSE block at same index
        if idx < len(else_blocks):
            else_body = else_blocks[idx]
            stmts = [s.strip() for s in else_body.split(";") if s.strip()]
            for stmt in stmts:
                if stmt.startswith("cout"):
                    output += check_prints(stmt + ";", vars_dict)
            return output

    return output


# Evaluate full C++-like code
def evaluate_output(code: str):
    try:
        v_dict = extract_vars(code)
    except Exception as e:
        return {
            "success": False,
            "error": f"Invalid variable declaration: {str(e)}",
            "output": "",
            "variables": {}
        }

    trimmed = code.strip()

    #  Reject pure numbers like "16"
    if re.fullmatch(r"\d+", trimmed):
        return {"success": False, "error": "This is not valid C++ code. You must declare a variable and print it with cout."}

    #  Reject code that has no semicolon
    if ";" not in code:
        return {"success": False, "error": "Missing semicolon — this is not valid C++ code."}

    #  Reject code that never declares a variable
    if not re.search(r"(int|string|float)\s+\w+\s*=", code):
        return {"success": False, "error": "You must declare a variable using int, string, or float."}

    #  Reject code without cout
    if "cout" not in code:
        return {"success": False, "error": "You must print output using cout."}

    # Try to evaluate prints
    try:
        output = check_prints(code, v_dict)

        # simulate if/else
        if_output = simulate_if_statements(code, v_dict)

        #remove wrongly printed unconditional couts
        base_output = ""

    except Exception as e:
        return {
            "success": False,
            "error": f"...",
            "output": "",
            "variables": {},
            "loop_trace": []
    }
    # 1. RAW STUDENT OUTPUT
    try:
        raw_output = check_prints(code, v_dict)
    except:
        raw_output = ""

    # 2. SIMULATION
    if_output = simulate_if_statements(code, v_dict)
    for_output = simulate_for_loops(code, v_dict)
    loop_output = simulate_while_loops(code, v_dict)

    # 3. FINAL OUTPUT
    final_output = for_output + loop_output + if_output


    return {
    "success": True,
    "output": final_output,
    "raw_output": raw_output,
    "variables": v_dict,
    "loop_trace": []
    }


def generate_expected_output(task):
    scope = dict(task["init_values"])
    output = ""

    while eval(task["condition"], {}, scope):
        cout = task["cout_template"] + str(scope["i"])
        output += cout

        # apply updates
        updates = task["update"]
        if not isinstance(updates, list):
            updates = [updates]

        for upd in updates:
            exec(upd, {}, scope)

    return output





















