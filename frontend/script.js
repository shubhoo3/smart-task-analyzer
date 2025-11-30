const textarea = document.getElementById("tasks-json");
const analyzeBtn = document.getElementById("analyze-btn");
const suggestBtn = document.getElementById("suggest-btn");
const loadSampleBtn = document.getElementById("load-sample");
const strategySelect = document.getElementById("strategy-select");
const resultsEl = document.getElementById("results");
const summaryEl = document.getElementById("summary");
const statusEl = document.getElementById("status");

const API_BASE = "http://127.0.0.1:8000/api/tasks";

function setStatus(message, isError = false) {
    statusEl.textContent = message || "";
    statusEl.style.color = isError ? "#f97373" : "#9ca3af";
}

function loadSample() {
    const sample = [
        {
            title: "Finish Smart Task Analyzer core logic",
            due_date: "2025-12-01",
            estimated_hours: 3,
            importance: 9,
            dependencies: [],
        },
        {
            title: "Refactor old side project",
            due_date: "2025-12-20",
            estimated_hours: 6,
            importance: 5,
            dependencies: [],
        },
        {
            title: "Pay electricity bill",
            due_date: "2025-11-28",
            estimated_hours: 0.5,
            importance: 10,
            dependencies: [],
        },
        {
            title: "Write blog post about Django tips",
            due_date: "2026-01-10",
            estimated_hours: 4,
            importance: 6,
            dependencies: ["outline"],
        },
    ];

    textarea.value = JSON.stringify(sample, null, 2);
    setStatus("Loaded sample tasks.");
}

function parseTasksFromTextarea() {
    const raw = textarea.value.trim();
    if (!raw) {
        return [];
    }
    try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
            return parsed;
        }
        if (Array.isArray(parsed.tasks)) {
            return parsed.tasks;
        }
        throw new Error("JSON must be an array of tasks or an object with a 'tasks' array.");
    } catch (err) {
        throw new Error("Invalid JSON: " + err.message);
    }
}

function classifyScore(score) {
    if (score >= 8) return "high";
    if (score >= 4) return "medium";
    return "low";
}

function renderResults(data, fromSuggest = false) {
    const tasks = data.tasks || [];
    resultsEl.innerHTML = "";

    if (fromSuggest) {
        summaryEl.textContent = data.summary || "";
    } else {
        summaryEl.textContent = tasks.length
            ? `Showing ${tasks.length} tasks sorted by priority.`
            : "No tasks to display.";
    }

    tasks.forEach((task, index) => {
        const card = document.createElement("div");
        card.className = "task-card";

        const header = document.createElement("div");
        header.className = "task-header";

        const title = document.createElement("div");
        title.className = "task-title";
        title.textContent = task.title || `Task ${index + 1}`;

        const importance = Number(task.importance ?? 5);
        const importanceLevel = importance >= 8 ? "high" : importance >= 4 ? "medium" : "low";

        const badge = document.createElement("span");
        badge.className = `badge badge-${importanceLevel}`;
        badge.textContent = `Imp ${importance}`;

        header.appendChild(title);
        header.appendChild(badge);

        const meta = document.createElement("div");
        meta.className = "meta";
        const due = task.due_date || "No due date";
        const hours = task.estimated_hours ?? "?";
        const deps = Array.isArray(task.dependencies) ? task.dependencies.length : 0;
        meta.textContent = `Due: ${due} • Est: ${hours}h • Deps: ${deps}`;

        const score = Number(task._score ?? 0).toFixed(2);
        const scoreLevel = classifyScore(Number(score));
        const scoreEl = document.createElement("div");
        scoreEl.className = `score score-${scoreLevel}`;
        scoreEl.textContent = `Score: ${score}`;

        const expl = document.createElement("div");
        expl.className = "explanation";
        expl.textContent = task._explanation || "";

        card.appendChild(header);
        card.appendChild(meta);
        card.appendChild(scoreEl);
        card.appendChild(expl);
        resultsEl.appendChild(card);
    });
}

async function callApi(path, body) {
    const url = `${API_BASE}/${path}`;
    const opts = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    };

    const resp = await fetch(url, opts);
    if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`HTTP ${resp.status}: ${text}`);
    }
    return resp.json();
}

async function handleAnalyze() {
    setStatus("Analyzing tasks...");
    try {
        const tasks = parseTasksFromTextarea();
        if (!tasks.length) {
            setStatus("Please enter at least one task.", true);
            return;
        }
        const strategy = strategySelect.value;
        const data = await callApi("analyze/", { tasks, strategy });
        renderResults(data, false);
        setStatus("Analysis complete.");
    } catch (err) {
        setStatus(err.message, true);
    }
}

async function handleSuggest() {
    setStatus("Requesting suggestions...");
    try {
        const tasks = parseTasksFromTextarea();
        if (!tasks.length) {
            setStatus("Please enter at least one task.", true);
            return;
        }
        const data = await callApi("suggest/", { tasks });
        renderResults(data, true);
        setStatus("Suggestions ready.");
    } catch (err) {
        setStatus(err.message, true);
    }
}

loadSampleBtn.addEventListener("click", loadSample);
analyzeBtn.addEventListener("click", handleAnalyze);
suggestBtn.addEventListener("click", handleSuggest);

// Initialize with sample data to make first run easy
loadSample();
