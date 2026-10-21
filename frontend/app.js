
const API_BASE = "http://127.0.0.1:8000";

const form = document.getElementById("assessment-form");
const submitButton = document.getElementById("submit-button");
const statementInput = document.getElementById("statement");
const charCount = document.getElementById("char-count");
const reliabilityInput = document.getElementById("reliability");
const reliabilityValue = document.getElementById("reliability-value");

const apiStatus = document.getElementById("api-status");
const apiDetail = document.getElementById("api-detail");
const headerStatusText = document.getElementById("header-status-text");
const connectionIndicator = document.getElementById("connection-indicator");

const resultsEmpty = document.getElementById("results-empty");
const resultsContent = document.getElementById("results-content");
const resultSummary = document.getElementById("result-summary");
const resultMetrics = document.getElementById("result-metrics");
const claimList = document.getElementById("claim-list");
const errorBox = document.getElementById("error-box");
const toast = document.getElementById("toast");

const historyTableBody = document.getElementById("history-table-body");

// AI Assistant elements
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatSendButton = document.getElementById("chat-send-button");
const clearChatButton = document.getElementById("clear-chat");

let latestAssessment = null;
let toastTimer = null;
let apiIsOnline = false;
let assessmentHistory = [];

const STATUSES = {
  supported: "SUPPORTED",
  contradicted: "CONTRADICTED",
  mixed: "MIXED",
  insufficient: "INSUFFICIENT_EVIDENCE"
};

// -----------------------------------------
// Toast notifications
// -----------------------------------------

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");

  clearTimeout(toastTimer);

  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// -----------------------------------------
// API connection status
// -----------------------------------------

function setApiStatus(online, detail) {
  apiIsOnline = online;

  apiStatus.replaceChildren();
  apiStatus.appendChild(
    document.createTextNode(online ? "Connected" : "Offline")
  );

  const dot = document.createElement("span");
  dot.className = `status-dot ${online ? "online" : "offline"}`;
  dot.setAttribute("aria-hidden", "true");

  apiStatus.appendChild(dot);
  apiDetail.textContent = detail;

  if (headerStatusText) {
    headerStatusText.textContent = online
      ? "Local API connected"
      : "Local API unavailable";
  }

  if (connectionIndicator) {
    connectionIndicator.replaceChildren();

    const indicatorDot = document.createElement("span");
    indicatorDot.className = `status-dot ${online ? "online" : "offline"}`;
    indicatorDot.setAttribute("aria-hidden", "true");

    connectionIndicator.appendChild(indicatorDot);
  }
}

async function checkApi() {
  try {
    const response = await fetch(`${API_BASE}/`, {
      method: "GET"
    });

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    setApiStatus(true, "FastAPI is reachable on this device.");
  } catch {
    setApiStatus(false, "Start the local FastAPI server to connect.");
  }
}

// -----------------------------------------
// Error handling
// -----------------------------------------

function hideResultsError() {
  errorBox.classList.add("hidden");
  errorBox.textContent = "";
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
  resultsEmpty.classList.add("hidden");
  resultsContent.classList.add("hidden");
}

// -----------------------------------------
// Assessment status helpers
// -----------------------------------------

function statusClass(status) {
  return String(status || "")
    .toLowerCase()
    .replaceAll("_", "-");
}

function prettyStatus(status) {
  return String(status || "UNKNOWN").replaceAll("_", " ");
}

// -----------------------------------------
// Assessment metrics
// -----------------------------------------

function makeMetric(value, label, extraClass) {
  const card = document.createElement("div");
  card.className = `metric ${extraClass || ""}`;

  const number = document.createElement("strong");
  number.textContent = value ?? 0;

  const text = document.createElement("span");
  text.textContent = label;

  card.append(number, text);

  return card;
}

function updateStatistics(data) {
  const values = [
    ["stat-supported", data.supported_claims],
    ["stat-contradicted", data.contradicted_claims],
    ["stat-mixed", data.mixed_claims],
    ["stat-insufficient", data.insufficient_evidence_claims]
  ];

  values.forEach(([id, value]) => {
    const element = document.getElementById(id);

    if (element) {
      element.textContent = value ?? 0;
    }
  });
}

// -----------------------------------------
// Render assessment results
// -----------------------------------------

function renderAssessment(data) {
  latestAssessment = data;

  resultsEmpty.classList.add("hidden");
  errorBox.classList.add("hidden");
  resultsContent.classList.remove("hidden");

  resultSummary.textContent =
    data.summary || "Assessment completed. Review each claim below.";

  resultMetrics.replaceChildren(
    makeMetric(data.supported_claims, "Supported", "supported"),
    makeMetric(data.contradicted_claims, "Contradicted", "contradicted"),
    makeMetric(data.mixed_claims, "Mixed", "mixed"),
    makeMetric(
      data.insufficient_evidence_claims,
      "Insufficient evidence",
      "insufficient"
    )
  );

  updateStatistics(data);

  claimList.replaceChildren();

  if (!Array.isArray(data.results) || data.results.length === 0) {
    const empty = document.createElement("p");
    empty.className = "claim-reason";
    empty.textContent = "No claim-level results were returned.";
    claimList.appendChild(empty);
    return;
  }

  data.results.forEach((item) => {
    const card = document.createElement("article");
    card.className = "claim-card";

    const top = document.createElement("div");
    top.className = "claim-top";

    const id = document.createElement("span");
    id.className = "claim-id";
    id.textContent = item.claim_id || "Claim";

    const badge = document.createElement("span");
    badge.className = `status-badge status-${statusClass(item.status)}`;
    badge.textContent = prettyStatus(item.status);

    top.append(id, badge);

    const reason = document.createElement("p");
    reason.className = "claim-reason";
    reason.textContent =
      item.reason || "No explanation was provided.";

    card.append(top, reason);

    const metaParts = [];

    if (item.evidence_id) {
      metaParts.push(`Evidence: ${item.evidence_id}`);
    }

    if (item.confidence !== null && item.confidence !== undefined) {
      metaParts.push(`Engine confidence: ${item.confidence}`);
    }

    if (metaParts.length > 0) {
      const meta = document.createElement("div");
      meta.className = "claim-meta";
      meta.textContent = metaParts.join(" · ");
      card.appendChild(meta);
    }

    claimList.appendChild(card);
  });
}

// -----------------------------------------
// Recent assessments
// -----------------------------------------

function renderHistory() {
  if (!historyTableBody) return;

  historyTableBody.replaceChildren();

  if (assessmentHistory.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = 3;
    cell.className = "table-empty";
    cell.textContent = "No assessments in this session.";

    row.appendChild(cell);
    historyTableBody.appendChild(row);

    return;
  }

  assessmentHistory.forEach((record) => {
    const row = document.createElement("tr");

    const statementCell = document.createElement("td");
    statementCell.textContent = record.statementId;

    const caseCell = document.createElement("td");
    caseCell.textContent = record.caseId;

    const statusCell = document.createElement("td");
    const badge = document.createElement("span");

    badge.className = `status-badge status-${statusClass(record.status)}`;
    badge.textContent = prettyStatus(record.status);

    statusCell.appendChild(badge);
    row.append(statementCell, caseCell, statusCell);

    historyTableBody.appendChild(row);
  });
}

function addHistoryRecord(statementId, caseId, data) {
  const results = Array.isArray(data.results) ? data.results : [];

  let status = "NOT_AVAILABLE";

  if (results.length === 1) {
    status = results[0].status || status;
  } else if (results.length > 1) {
    const statuses = [...new Set(results.map((item) => item.status))];

    status = statuses.length === 1 ? statuses[0] : "MIXED";
  }

  assessmentHistory.unshift({
    statementId,
    caseId,
    status
  });

  renderHistory();
}

// -----------------------------------------
// API validation errors
// -----------------------------------------

function validationMessage(payload, status) {
  if (Array.isArray(payload?.detail)) {
    const messages = payload.detail.map((item) => {
      const field = Array.isArray(item.loc)
        ? item.loc.slice(1).join(" → ")
        : "input";

      return `${field || "input"}: ${item.msg || "invalid value"}`;
    });

    return `Please check the request fields (HTTP ${status}). ${messages.join("; ")}`;
  }

  if (typeof payload?.detail === "string") {
    return payload.detail;
  }

  return `The API request failed (HTTP ${status}). Check the backend and request fields.`;
}

// -----------------------------------------
// AI Assistant chat
// -----------------------------------------

// -----------------------------------------
// Safe Markdown formatting for AI responses
// -----------------------------------------

function appendFormattedText(container, text) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);

  parts.forEach((part) => {
    const boldMatch = part.match(/^\*\*(.+)\*\*$/);

    if (boldMatch) {
      const strong = document.createElement("strong");
      strong.textContent = boldMatch[1];
      container.appendChild(strong);
    } else if (part) {
      container.appendChild(document.createTextNode(part));
    }
  });
}

function renderFormattedResponse(container, message) {
  container.replaceChildren();

  const lines = String(message || "").split(/\r?\n/);

  let paragraphLines = [];
  let listContainer = null;
  let listType = null;

  function flushParagraph() {
    if (paragraphLines.length === 0) return;

    const paragraph = document.createElement("p");
    paragraph.className = "chat-paragraph";

    appendFormattedText(
      paragraph,
      paragraphLines.join(" ")
    );

    container.appendChild(paragraph);
    paragraphLines = [];
  }

  function closeList() {
    listContainer = null;
    listType = null;
  }

  function flushList() {
    if (listContainer) {
      container.appendChild(listContainer);
      closeList();
    }
  }

  lines.forEach((line) => {
    const trimmed = line.trim();

    // Empty line: finish the current paragraph or list.
    if (!trimmed) {
      flushParagraph();
      flushList();
      return;
    }

    // Markdown headings: # Heading, ## Heading, etc.
    const headingMatch = trimmed.match(/^#{1,6}\s+(.+)$/);

    if (headingMatch) {
      flushParagraph();
      flushList();

      const heading = document.createElement("h4");
      heading.className = "chat-response-heading";

      appendFormattedText(heading, headingMatch[1]);

      container.appendChild(heading);
      return;
    }

    // Bullet lists: - item, * item, or • item.
    const bulletMatch = trimmed.match(/^[-*•]\s+(.+)$/);

    // Numbered lists: 1. item, 2. item, etc.
    const numberedMatch = trimmed.match(/^\d+[.)]\s+(.+)$/);

    if (bulletMatch || numberedMatch) {
      flushParagraph();

      const currentType = numberedMatch ? "ol" : "ul";

      if (listType !== currentType) {
        flushList();

        listType = currentType;
        listContainer = document.createElement(currentType);
        listContainer.className = "chat-response-list";
      }

      const item = document.createElement("li");

      appendFormattedText(
        item,
        bulletMatch ? bulletMatch[1] : numberedMatch[1]
      );

      listContainer.appendChild(item);
      return;
    }

    // Normal text.
    flushList();
    paragraphLines.push(trimmed);
  });

  flushParagraph();
  flushList();
}

// -----------------------------------------
// AI Assistant chat messages
// -----------------------------------------

function addChatMessage(message, role) {
  if (!chatMessages) return null;

  const bubble = document.createElement("div");
  bubble.className = `chat-message ${role}-message`;

  const content = document.createElement("div");
  content.className = "chat-message-content";

  if (role === "assistant") {
    renderFormattedResponse(content, message);
  } else {
    // User messages and errors remain plain text.
    content.textContent = message;
  }

  bubble.appendChild(content);
  chatMessages.appendChild(bubble);

  chatMessages.scrollTop = chatMessages.scrollHeight;

  return bubble;
}

function resetChat() {
  if (!chatMessages) return;

  chatMessages.replaceChildren();

  const welcome = document.createElement("div");
  welcome.className = "chat-message assistant-message";
  welcome.textContent =
    "Hello! I'm the ASHWATHAMA AI Assistant. I can answer general questions and explain assessment results. I will not determine guilt or claim to reliably detect deception.";

  chatMessages.appendChild(welcome);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getChatErrorMessage(payload, status) {
  if (typeof payload?.detail === "string" && payload.detail.trim()) {
    return payload.detail;
  }

  if (Array.isArray(payload?.detail)) {
    return payload.detail
      .map((item) => item.msg || "Invalid request")
      .join("; ");
  }

  if (status === 502) {
    return "The AI service could not complete the request. Please try again in a moment.";
  }

  return `The chat request failed (HTTP ${status}). Please check the API and try again.`;
}

if (chatForm && chatInput && chatMessages && chatSendButton) {
  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = chatInput.value.trim();

    if (!question) {
      showToast("Please enter a message first.");
      return;
    }

    if (question.length > 2000) {
      showToast("Please keep your message under 2000 characters.");
      return;
    }

    addChatMessage(question, "user");

    chatInput.value = "";
    chatInput.disabled = true;
    chatSendButton.disabled = true;
    chatSendButton.textContent = "Thinking...";

    const typingMessage = addChatMessage(
      "ASHWATHAMA AI is preparing a response...",
      "typing"
    );

    try {
      const requestBody = { question };

      // Send the latest assessment as context when available.
      if (latestAssessment) {
        requestBody.assessment = latestAssessment;
      }

      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json"
        },
        body: JSON.stringify(requestBody)
      });

      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(getChatErrorMessage(payload, response.status));
      }

      if (typingMessage) {
        typingMessage.remove();
      }

      if (typeof payload.answer !== "string" || !payload.answer.trim()) {
        throw new Error(
          "The AI service returned an empty response. Please try again."
        );
      }

      addChatMessage(payload.answer, "assistant");
    } catch (error) {
      if (typingMessage) {
        typingMessage.remove();
      }

      addChatMessage(
        error.message ||
          "Could not connect to the AI Assistant. Check that FastAPI is running.",
        "error"
      );
    } finally {
      chatInput.disabled = false;
      chatSendButton.disabled = false;
      chatSendButton.textContent = "Send";
      chatInput.focus();
    }
  });

  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      chatForm.requestSubmit();
    }
  });
}

if (clearChatButton) {
  clearChatButton.addEventListener("click", () => {
    resetChat();
    showToast("Chat cleared.");
  });
}

// -----------------------------------------
// Submit assessment
// -----------------------------------------

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideResultsError();

  const statementId = document.getElementById("statement-id").value.trim();
  const caseId = document.getElementById("case-id").value.trim();
  const statement = statementInput.value.trim();
  const eventTime = document.getElementById("event-time").value;
  const reliability = Number(reliabilityInput.value);

  if (!statementId || !caseId || !statement || !eventTime) {
    showError(
      "Please complete Statement ID, Case ID, Statement, and Event Time."
    );
    return;
  }

  const evidence = {
    case_id: caseId,
    evidence_id: document.getElementById("evidence-id").value.trim(),
    source_device: document.getElementById("source-device").value,
    artifact_type: document.getElementById("artifact-type").value,
    event_time: eventTime,
    description: document.getElementById("description").value.trim(),
    source_tool: document.getElementById("source-tool").value.trim(),
    reliability,
    metadata: {},
    collection_method: "manual_test_entry"
  };

  const sourceReference = document
    .getElementById("source-reference")
    .value.trim();

  if (sourceReference) {
    evidence.source_reference = sourceReference;
  }

  if (
    !evidence.evidence_id ||
    !evidence.description ||
    !evidence.source_tool
  ) {
    showError(
      "Please fill in Evidence ID, Evidence Description, and Source / Tool."
    );
    return;
  }

  const buttonLabel = submitButton.querySelector("span");
  const arrow = submitButton.querySelector(".button-arrow");

  submitButton.disabled = true;
  buttonLabel.textContent = "Analyzing...";
  arrow.textContent = "...";

  try {
    const response = await fetch(`${API_BASE}/assess`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
      },
      body: JSON.stringify({
        statement_id: statementId,
        statement,
        evidence: [evidence]
      })
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      if (response.status >= 500) {
        throw new Error(
          "Assessment failed because of a server error. Check the backend terminal."
        );
      }

      throw new Error(validationMessage(payload, response.status));
    }

    renderAssessment(payload);
    addHistoryRecord(statementId, caseId, payload);

    showToast("Assessment completed. Review the findings.");

    document.getElementById("results-panel").scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  } catch (error) {
    showError(
      error.message ||
        "Could not connect to the API. Check that FastAPI is running at http://127.0.0.1:8000."
    );
  } finally {
    submitButton.disabled = false;
    buttonLabel.textContent = "Run Assessment";
    arrow.textContent = "→";
  }
});

// -----------------------------------------
// Statement character count
// -----------------------------------------

statementInput.addEventListener("input", () => {
  const length = statementInput.value.length;

  charCount.textContent =
    `${length} character${length === 1 ? "" : "s"}`;
});

// -----------------------------------------
// Reliability slider
// -----------------------------------------

reliabilityInput.addEventListener("input", () => {
  const value = Number(reliabilityInput.value).toFixed(2);

  reliabilityValue.value = value;
  reliabilityValue.textContent = value;
});

// -----------------------------------------
// Copy assessment JSON
// -----------------------------------------

document.getElementById("copy-results").addEventListener("click", async () => {
  if (!latestAssessment) {
    showToast("No assessment results are available to copy.");
    return;
  }

  try {
    await navigator.clipboard.writeText(
      JSON.stringify(latestAssessment, null, 2)
    );

    showToast("Assessment JSON copied to clipboard.");
  } catch {
    showToast("Clipboard access is unavailable in this browser context.");
  }
});


// -----------------------------------------
// Mobile navigation
// -----------------------------------------

const sidebar = document.getElementById("sidebar");
const mobileMenu = document.getElementById("mobile-menu");

mobileMenu.addEventListener("click", () => {
  const isOpen = sidebar.classList.toggle("open");

  mobileMenu.setAttribute("aria-expanded", String(isOpen));
  mobileMenu.setAttribute(
    "aria-label",
    isOpen ? "Close navigation" : "Open navigation"
  );
});

document.querySelectorAll(".nav-item").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((nav) => {
      nav.classList.remove("active");
    });

    item.classList.add("active");

    const section = item.dataset.section;
    const assistantSection = document.getElementById("ai-assistant");

    // Show the assistant only when its navigation item is selected.
    if (assistantSection) {
      assistantSection.classList.toggle(
        "active",
        section === "ai-assistant"
      );
    }

    const destinations = {
      home: document.getElementById("home"),
      assessment: document.getElementById("assessment-section"),
      history: document.getElementById("history-section"),
      "ai-assistant": assistantSection,
      evidence: document.getElementById("assessment-section"),
      reports: document.getElementById("results-panel")
    };

    const destination = destinations[section];

    if (destination) {
      destination.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }

    if (window.innerWidth <= 760) {
      sidebar.classList.remove("open");
      mobileMenu.setAttribute("aria-expanded", "false");
      mobileMenu.setAttribute("aria-label", "Open navigation");
    }

    if (section === "evidence" || section === "reports") {
      showToast(
        section === "evidence"
          ? "Evidence Repository is not yet a separate module."
          : "Report generation is not yet implemented."
      );
    }
  });
});

// -----------------------------------------
// Prototype notice
// -----------------------------------------

document.getElementById("theme-note").addEventListener("click", () => {
  showToast(
    "Prototype mode: use synthetic or authorized evidence only."
  );
});

// -----------------------------------------
// Initial setup
// -----------------------------------------

updateStatistics({
  supported_claims: 0,
  contradicted_claims: 0,
  mixed_claims: 0,
  insufficient_evidence_claims: 0
});

renderHistory();
resetChat();
checkApi();
setInterval(checkApi, 30000);