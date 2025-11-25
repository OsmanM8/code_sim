import { useState } from "react";
import Editor from "@monaco-editor/react";
import { useCallback } from "react";
import Particles from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
console.log("Particles component loaded");
console.log("loadSlim:", loadSlim);


const lessons = [
  { id: "lesson1", title: "Lesson 1: Variables" },
  { id: "lesson2", title: "Lesson 2: Strings" },
  { id: "lesson3", title: "Lesson 3: If Statements" },
  { id: "lesson4", title: "Lesson 4: Loops" },
  { id: "lesson5", title: "Lesson 5: Nested Loops" },
];

const lessonDescriptions = {
  lesson1: {
    title: "Lesson 1 — Variables",
    text: `In this lesson, you will learn how to declare and print variables in C++.

Your task:
- Declare at least one variable
- Assign it a value
- Print the value using cout

Example:
int age = 16;
cout << age;`
  },

  lesson2: {
    title: "Lesson 2 — Strings",
    text: `In this lesson, you will work with C++ strings.

Your task:
- Declare a string
- Assign it a word or name
- Print it using cout

Example:
string name = "Alex";
cout << name;`
  },

  lesson3: {
    title: "Lesson 3 — If Statements",
    text: `You will practice creating basic if/else logic.

Your task:
- Write an if statement
- Print something based on the condition

Example:
int x = 10;
if (x > 5) {
    cout << "Large";
}`
  },

  lesson4: {
    title: "Lesson 4 — Loops",
    text: `This lesson focuses on for-loops and while-loops.

Your task:
- Create a loop that prints something each iteration
- Use cout with text + the iteration number

Example:
for (int i = 0; i < 3; i++) {
    cout << "Iteration " << i;
}`
  },

  lesson5: {
    title: "Lesson 5 — Nested Loops",
    text: `Practice loops inside loops.

Your task:
- Create an outer loop and inner loop
- Print values from both

Example:
for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 2; j++) {
        cout << i << "," << j;
    }
}`
  }
};


export default function App() {
  const [selectedLesson, setSelectedLesson] = useState("lesson1");
  const [code, setCode] = useState("");
  const [output, setOutput] = useState("");

  const runCode = async () => {
    setOutput("Running...");
    try {
      const res = await fetch("https://codesim-gcpb.onrender.com/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lesson_id: selectedLesson,
          code: code,
        }),
      });

      const data = await res.json();
      console.log(data);

      if (data && data.feedback) {
        setOutput(
          data.success
            ? `✔ Passed\n\nOutput:\n${data.output}`
            : `✘ Failed\n\nFeedback:\n${data.feedback}\n\nYour Output:\n${data.your_output}`
        );
      } else {
        setOutput("Unexpected response from server.");
      }
    } catch (err) {
      setOutput("Error contacting server.");
    }
  };

  const particlesInit = useCallback(async (engine) => {
  await loadSlim(engine);
}, []);

const particlesLoaded = useCallback(async () => {}, []);


  return (
  <div className="flex h-screen bg-gradient-to-b from-[#000000] to-[#0f1629] text-gray-200">
    <Particles
  id="tsparticles"
  init={particlesInit}
  loaded={particlesLoaded}
  className="absolute inset-0 -z-10"
  options={{
    background: { color: "#0d0d0d" },
    fpsLimit: 60,
    particles: {
      number: { value: 60, density: { enable: true, area: 800 } },
      color: { value: "#ffffff" },
      links: {
        enable: true,
        color: "#ffffff66",
        distance: 140,
        opacity: 0.4,
        width: 1,
      },
      move: {
        enable: true,
        speed: 1,
        outModes: { default: "bounce" },
      },
      size: { value: { min: 1, max: 3 } },
      opacity: { value: 0.5 },
    },
    interactivity: {
      events: { onHover: { enable: true, mode: "repulse" } },
      modes: { repulse: { distance: 120 } },
    },
  }}
/>

    {/* Sidebar */}
    <div className="w-64 bg-gradient-to-b from-[#000000] to-[#0f1629] text-white p-5 flex flex-col gap-4 shadow-xl relative">
      <h1 className="text-3xl font-light tracking-[0.15em] uppercase mb-6 text-blue-300 drop-shadow-[0_0_6px_#3b82f6]">
        CodeSim
      </h1>

      {lessons.map((lesson) => (
        <button
          key={lesson.id}
          onClick={() => setSelectedLesson(lesson.id)}
          className={`text-left p-3 rounded-xl transition-all duration-200 ${
            selectedLesson === lesson.id
              ? "bg-blue-600 shadow-lg shadow-blue-500/40"
              : "bg-[#1a2332] hover:bg-[#223045] hover:shadow-md"
          }`}
        >
          {lesson.title}
        </button>
      ))}

      {/* Slim modern separator bar */}
      <div className="absolute top-0 right-0 w-[2px] h-full bg-white/10"></div>
    </div>



    {/* Main Content */}
    <div className="flex-1 p-8 flex gap-6 relative">
      
      {/* Lesson + Editor */}
      <div className="flex-1 flex flex-col">
        
        {/* Lesson Description */}
        <div className="mb-4 bg-white/10 backdrop-blur-md p-5 border border-white/20 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-2 text-blue-300">
            {lessonDescriptions[selectedLesson].title}
          </h2>
          <p className="text-sm whitespace-pre-line text-gray-200">
            {lessonDescriptions[selectedLesson].text}
          </p>
        </div>

        <h2 className="text-lg font-semibold mb-2 text-blue-300">Code Editor</h2>

        <div className="rounded-xl overflow-hidden shadow-[0_0_15px_#1e3a8a] border border-blue-800/30">
          <Editor
            height="420px"
            defaultLanguage="cpp"
            value={code}
            onChange={(value) => setCode(value)}
            theme="vs-dark"
          />
        </div>

        <button
          onClick={runCode}
          className="mt-5 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/30"
        >
          Run Code
        </button>
      </div>



      {/* Output Panel */}
      <div className="w-1/3 flex flex-col">
        <h2 className="text-lg font-semibold mb-2 text-blue-300">Output</h2>

        <pre className="flex-1 p-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl shadow-inner whitespace-pre-wrap text-gray-100">
          {output}
        </pre>
      </div>
    </div>
  </div>
);
}
