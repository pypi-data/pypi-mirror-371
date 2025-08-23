console.log("whisp ui loaded");

document.addEventListener("DOMContentLoaded", function () {
    const connectionsTbody = document.getElementById("connections-tbody");
    const connectionsCount = document.getElementById("connections-count");
    const messagesTbody = document.getElementById("messages-tbody");
    const pauseToggle = document.getElementById("pause-toggle");
    const clearBtn = document.getElementById("clear-btn");

    // ring buffer for last 20 messages
    const lastMessages = [];
    let isPaused = false;
    let rafPending = false;

    function setEmptyRow(tbody, text, cols) {
        tbody.innerHTML = "";
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = cols;
        td.className = "px-4 py-3 text-gray-500";
        td.textContent = text;
        tr.appendChild(td);
        tbody.appendChild(tr);
    }

    function addCell(tr, text, className) {
        const td = document.createElement("td");
        td.className = className || "px-4 py-2";
        td.textContent = text;
        tr.appendChild(td);
        return td;
    }

    function safeJsonPreview(obj) {
        try {
            return JSON.stringify(obj);
        } catch (e) {
            return "[unserializable]";
        }
    }

    function formatTimestamp(value) {
        // supports seconds or milliseconds
        const ms = value < 1e12 ? value * 1000 : value;
        const d = new Date(ms);
        // HH:MM:SS.mmm
        const h = String(d.getHours()).padStart(2, "0");
        const m = String(d.getMinutes()).padStart(2, "0");
        const s = String(d.getSeconds()).padStart(2, "0");
        const ms3 = String(d.getMilliseconds()).padStart(3, "0");
        return h + ":" + m + ":" + s + "." + ms3;
    }

    function renderConnections(connections) {
        if (!connectionsTbody) return;
        connectionsTbody.innerHTML = "";

        const entries = Object.entries(connections).filter(([sid, c]) => c && c.name);
        connectionsCount.textContent = String(entries.length);

        if (entries.length === 0) {
            setEmptyRow(connectionsTbody, "No connections available.", 2);
            return;
        }

        const frag = document.createDocumentFragment();
        for (const [sid, c] of entries) {
            const tr = document.createElement("tr");
            tr.className = "hover:bg-gray-50";
            addCell(tr, c.name || "N/A", "px-4 py-2 whitespace-nowrap");
            addCell(tr, c.sid, "px-4 py-2 font-mono text-xs break-all");
            frag.appendChild(tr);
        }
        connectionsTbody.appendChild(frag);
    }

    function safeJsonPretty(obj) {
        try {
            return JSON.stringify(obj, null, 2); // 2 spaces indent
        } catch (e) {
            return "[unserializable]";
        }
    }

    function renderMessages() {
        if (!messagesTbody) return;

        messagesTbody.innerHTML = "";
        if (lastMessages.length === 0) {
            setEmptyRow(messagesTbody, "No messages available.", 4);
            return;
        }

        const frag = document.createDocumentFragment();
        for (const msg of lastMessages) {
            const eventName = msg.event;
            const data = msg.data || {};

            const unixTs = data.time_stamp;
            const sender = data.sender || "N/A";
            const ts = typeof unixTs === "number" ? formatTimestamp(unixTs) : "";

            const copyData = Object.assign({}, data);
            delete copyData.time_stamp;
            delete copyData.sender;

            const tr = document.createElement("tr");
            tr.className = "hover:bg-gray-50 align-top";

            addCell(tr, ts, "px-4 py-2 whitespace-nowrap");
            addCell(tr, sender, "px-4 py-2 whitespace-nowrap");
            const eventTd = addCell(tr, "", "px-4 py-2 whitespace-nowrap");
            const badge = document.createElement("span");
            badge.textContent = eventName || "";
            badge.className = "inline-block text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-800 border border-gray-200";
            eventTd.appendChild(badge);

            const dataTd = addCell(tr, "", "px-4 py-2 align-top");
            const pre = document.createElement("pre");
            pre.className = "font-mono text-xs bg-gray-50 rounded p-2 overflow-x-auto whitespace-pre";
            pre.textContent = safeJsonPretty(copyData);
            dataTd.appendChild(pre);

            frag.appendChild(tr);
        }
        messagesTbody.appendChild(frag);
    }

    function scheduleRender() {
        if (rafPending) return;
        rafPending = true;
        requestAnimationFrame(() => {
            renderMessages();
            rafPending = false;
        });
    }

    // fetch current connections once and any time join/left arrives
    function fetchConnections() {
        fetch("/api/connections")
            .then(r => r.json())
            .then(renderConnections)
            .catch(err => {
                console.error("Error fetching connections:", err);
            });
    }

    // wire controls
    pauseToggle.addEventListener("change", () => {
        isPaused = pauseToggle.checked;
    });

    clearBtn.addEventListener("click", () => {
        lastMessages.length = 0;
        renderMessages();
    });

    // initial connections load
    fetchConnections();

    // websocket
    const client = new WhispClient();

    client.onMessage((message) => {
        if (!message || typeof message !== "object") return;
        if (!("event" in message)) return;

        const ev = message.event;

        if (ev === "whisp/joined" || ev === "whisp/left") {
            fetchConnections();
            return;
        }

        // keep last 20, newest first
        if (!isPaused) {
            lastMessages.unshift(message);
            if (lastMessages.length > 20) lastMessages.pop();
            scheduleRender();
        }
    });
});
