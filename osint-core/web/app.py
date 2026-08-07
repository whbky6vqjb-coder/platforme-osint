import asyncio
import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Platforme OSINT - Dashboard")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
log_queue = asyncio.Queue()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")

async def event_generator(request: Request):
    while True:
        if await request.is_disconnected():
            break
        try:
            log_entry = await asyncio.wait_for(log_queue.get(), timeout=1.0)
            yield f"data: {json.dumps(log_entry)}\n\n"
        except asyncio.TimeoutError:
            yield ": keepalive\n\n"

@app.get("/api/logs/stream")
async def stream_logs(request: Request):
    return StreamingResponse(event_generator(request), media_type="text/event-stream")

@app.post("/api/agent/stop")
async def stop_agent():
    with open(os.path.join(DATA_DIR, "STOP_SIGNAL"), "w") as f:
        f.write("STOP")
    return {"status": "Stop signal emitted"}

@app.get("/api/tools")
async def list_tools():
    from osint_core.tools import get_all_tools
    tools = {}
    for name, tool in get_all_tools().items():
        tools[name] = {
            "name": tool.name(),
            "description": tool.description(),
            "category": tool.category(),
            "requires_api_key": tool.requires_api_key(),
            "is_stealth": tool.is_stealth(),
        }
    return tools

@app.get("/api/entities")
async def list_entities():
    from osint_core.correlator import EntityCorrelator
    correlator = EntityCorrelator()
    return {"entities": correlator.get_all_entities()}

@app.get("/api/graph/mermaid")
async def get_mermaid_graph():
    from osint_core.graph.mermaid import MermaidGenerator
    generator = MermaidGenerator()
    return {"mermaid": generator.generate()}

@app.post("/api/investigate")
async def investigate(request_data: dict):
    from osint_core.engine.investigation import InvestigationEngine
    engine = InvestigationEngine()
    goal = request_data.get("goal", "")
    result = await engine.run(goal)
    return {
        "goal": result.goal,
        "confidence": result.confidence,
        "report": result.report,
        "mermaid": result.mermaid_diagram,
        "entities": [{"name": e.value, "type": e.type, "confidence": e.confidence} for e in result.correlated_entities],
    }

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Platforme OSINT - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0e17; color: #c8d6e5; font-family: 'JetBrains Mono', monospace; }
        .header { background: #1a1f2e; padding: 16px 24px; border-bottom: 1px solid #2a3a4e; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #00d4aa; font-size: 1.2em; }
        .status-bar { display: flex; gap: 16px; font-size: 0.8em; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
        .status-dot.green { background: #00ff88; }
        .main { display: grid; grid-template-columns: 250px 1fr 300px; gap: 0; height: calc(100vh - 60px); }
        .sidebar { background: #0f1520; border-right: 1px solid #2a3a4e; padding: 12px; overflow-y: auto; }
        .sidebar h3 { color: #00d4aa; font-size: 0.85em; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
        .sidebar a { display: block; color: #8899aa; padding: 6px 8px; text-decoration: none; font-size: 0.85em; border-radius: 4px; }
        .sidebar a:hover { background: #1a2a3e; color: #00d4aa; }
        .content { padding: 16px; overflow-y: auto; }
        .panel { background: #111827; border: 1px solid #2a3a4e; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
        .panel h2 { color: #00d4aa; font-size: 1em; margin-bottom: 12px; }
        .tool-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px; }
        .tool-card { background: #1a1f2e; border: 1px solid #2a3a4e; border-radius: 6px; padding: 10px; cursor: pointer; transition: border-color 0.2s; }
        .tool-card:hover { border-color: #00d4aa; }
        .tool-card .tool-name { color: #e0e0e0; font-weight: bold; font-size: 0.85em; }
        .tool-card .tool-cat { color: #667788; font-size: 0.7em; margin-top: 4px; }
        .tool-card .tool-status { margin-top: 6px; font-size: 0.75em; color: #00ff88; }
        .input-area { display: flex; gap: 8px; margin-top: 12px; }
        .input-area input { flex: 1; background: #1a1f2e; border: 1px solid #2a3a4e; color: #c8d6e5; padding: 8px 12px; border-radius: 4px; font-family: inherit; }
        .input-area button { background: #00d4aa; color: #0a0e17; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; font-family: inherit; }
        .input-area button:hover { background: #00ff88; }
        .log-console { background: #000; border: 1px solid #2a3a4e; border-radius: 6px; padding: 10px; height: 300px; overflow-y: auto; font-size: 0.8em; }
        .log-entry { padding: 2px 0; border-bottom: 1px solid #1a1a2e; }
        .log-entry .timestamp { color: #556677; }
        .log-entry .level { font-weight: bold; }
        .log-entry .level.info { color: #00d4aa; }
        .log-entry .level.error { color: #ff4444; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Platforme OSINT - Dashboard</h1>
        <div class="status-bar">
            <span><span class="status-dot green"></span> Orchestrator</span>
            <span><span class="status-dot green"></span> Hermes-3</span>
            <span><span class="status-dot green"></span> Web UI</span>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <h3>Navigation</h3>
            <a href="#" onclick="showSection('investigate')">Nouvelle Investigation</a>
            <a href="#" onclick="showSection('tools')">Outils OSINT</a>
            <a href="#" onclick="showSection('graph')">Graphe d'Entites</a>
            <a href="#" onclick="showSection('reports')">Rapports</a>
            <h3 style="margin-top:16px">Categories</h3>
            <a href="#" onclick="filterTools('corporate')">Corporate</a>
            <a href="#" onclick="filterTools('sanctions')">Sanctions</a>
            <a href="#" onclick="filterTools('geolocation')">Geolocation</a>
            <a href="#" onclick="filterTools('leaks')">Fuites</a>
            <a href="#" onclick="filterTools('cyber')">Cyber</a>
            <a href="#" onclick="filterTools('digital')">Digital</a>
            <a href="#" onclick="filterTools('blockchain')">Blockchain</a>
            <a href="#" onclick="filterTools('media')">Media</a>
            <a href="#" onclick="filterTools('legal')">Legal</a>
            <a href="#" onclick="filterTools('ghost')">Projets Fantomes</a>
        </div>
        <div class="content" id="main-content">
            <div class="panel" id="section-investigate">
                <h2>Lancement d'Investigation</h2>
                <p>Entrez un objectif pour demarrer l'analyse OSINT automatique.</p>
                <div class="input-area">
                    <input type="text" id="investigation-query" placeholder="Ex: Trouver les infrastructures liees a l'entreprise X...">
                    <button onclick="startInvestigation()">Lancer</button>
                </div>
                <div class="log-console" id="investigation-log"></div>
            </div>
            <div class="panel" id="section-tools" style="display:none">
                <h2>Outils OSINT (200 integrés)</h2>
                <div class="tool-grid" id="tool-grid"></div>
            </div>
            <div class="panel" id="section-graph" style="display:none">
                <h2>Graphe d'Entites</h2>
                <div class="panel"><pre id="mermaid-output"></pre></div>
            </div>
            <div class="panel" id="section-reports" style="display:none">
                <h2>Rapports</h2>
                <div id="reports-list"></div>
            </div>
        </div>
        <div class="sidebar">
            <h3>Entites Detectees</h3>
            <div id="entity-list" style="font-size:0.8em;"></div>
            <h3 style="margin-top:16px">Session</h3>
            <div id="session-info" style="font-size:0.8em;color:#667788;"></div>
        </div>
    </div>
    <script>
        const sections = ['investigate','tools','graph','reports'];
        function showSection(id) {
            sections.forEach(s => {
                const el = document.getElementById('section-' + s);
                if (el) el.style.display = s === id ? 'block' : 'none';
            });
        }
        async function startInvestigation() {
            const query = document.getElementById('investigation-query').value;
            if (!query) return;
            const log = document.getElementById('investigation-log');
            log.innerHTML = '';
            addLog('info', 'Investigation demarree: ' + query);
            try {
                const resp = await fetch('/api/investigate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({goal: query})
                });
                const data = await resp.json();
                addLog('info', 'Investigation terminee. Confidence: ' + (data.confidence || 0).toFixed(2));
                addLog('info', 'Entites: ' + (data.entities ? data.entities.length : 0));
                if (data.mermaid) {
                    document.getElementById('mermaid-output').textContent = data.mermaid;
                }
            } catch (e) {
                addLog('error', 'Erreur: ' + e.message);
            }
        }
        function addLog(level, msg) {
            const log = document.getElementById('investigation-log');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            const ts = new Date().toISOString().slice(11, 19);
            entry.innerHTML = '<span class="timestamp">' + ts + '</span> <span class="level ' + level + '">[' + level.toUpperCase() + ']</span> ' + msg;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }
        async function loadTools() {
            try {
                const resp = await fetch('/api/tools');
                const tools = await resp.json();
                const grid = document.getElementById('tool-grid');
                grid.innerHTML = '';
                for (const [name, tool] of Object.entries(tools)) {
                    const card = document.createElement('div');
                    card.className = 'tool-card';
                    card.innerHTML = '<div class="tool-name">' + name + '</div><div class="tool-cat">' + (tool.category || '') + '</div><div class="tool-status">Disponible</div>';
                    grid.appendChild(card);
                }
            } catch (e) {
                console.error('Failed to load tools:', e);
            }
        }
        async function loadEntities() {
            try {
                const resp = await fetch('/api/entities');
                const data = await resp.json();
                const list = document.getElementById('entity-list');
                list.innerHTML = '';
                for (const entity of (data.entities || []).slice(0, 15)) {
                    const item = document.createElement('div');
                    item.style.cssText = 'padding:4px 0;border-bottom:1px solid #1a2a3e;';
                    item.innerHTML = '<span>' + entity.name + '</span> <span style="color:#667788">' + entity.type + '</span>';
                    list.appendChild(item);
                }
            } catch (e) {
                console.error('Failed to load entities:', e);
            }
        }
        async function loadGraph() {
            try {
                const resp = await fetch('/api/graph/mermaid');
                const data = await resp.json();
                document.getElementById('mermaid-output').textContent = data.mermaid || 'Aucun graphe disponible';
            } catch (e) {
                console.error('Failed to load graph:', e);
            }
        }
        loadTools();
        loadEntities();
        loadGraph();
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="error")
