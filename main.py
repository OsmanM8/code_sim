from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import validators
from lesson_validators import (
    lesson1_validator,
    lesson2_validator,
    lesson3_validator,
    lesson4_validator,
    lesson5_validator
)

# Import code execution engine
from Cpp_engine import evaluate_output

app = FastAPI()

# CORS - UPDATE THIS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://codesim-front.onrender.com"],  # Changed from localhost:3000 to *
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class CodeRequest(BaseModel):
    lesson_id: str
    code: str

# Expected outputs (from your existing dict)
lesson_expected_output = {
    "lesson1": "16",
    "lesson2": "Alex",
    "lesson3": "Large",
    "lesson4": "Iteration 0Iteration 1Iteration 2",
    "lesson5": "0,00,1,01,0,11,1,1"
}

# ✅ Your dictionary of validators
lesson_validators = {
    "lesson1": lesson1_validator,
    "lesson2": lesson2_validator,
    "lesson3": lesson3_validator,
    "lesson4": lesson4_validator,
    "lesson5": lesson5_validator,
}

@app.post("/validate")
async def validate_lesson(req: CodeRequest):
    lesson_id = req.lesson_id
    code = req.code

    print("🔥 USING ADVANCED VALIDATOR 🔥")

    # Make sure lesson ID is valid
    if lesson_id not in lesson_validators:
        raise HTTPException(status_code=400, detail="Invalid lesson ID.")

    # Run engine on code
    result = evaluate_output(code)

    if not result["success"]:
        return {
            "success": False,
            "feedback": result["error"],
            "your_output": "",
            "output": lesson_expected_output[lesson_id],
        }

    # Run lesson-specific validator
    validator = lesson_validators[lesson_id]
    ok, feedback = validator(code, result)

    # For lessons 1 and 2 → use raw_output only
    if lesson_id in ["lesson1", "lesson2"]:
        final_output = result["raw_output"]
    else:
        final_output = result["output"]

    return {
        "success": ok,
        "feedback": feedback,
        "output": final_output,
        "your_output": final_output,
    }
