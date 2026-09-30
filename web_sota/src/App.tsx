import { useCallback, useEffect, useState } from "react";
import FloatingChat from "./components/FloatingChat";

type Tab = "welcome" | "topics" | "archive" | "docs";

interface Topic {
  category: string;
  emoji: string;
  topic: string;
}

interface Category {
  name: string;
  emoji: string;
  count: number;
}

interface ArchiveEntry {
  id: string;
  topic: string;
  response: string;
  tags: string[];
  created_at: string;
}

interface DocsResult {
  score: number;
  content: string;
  relative_path?: string;
}

const NAV: { id: Tab; label: string; short: string }[] = [
  { id: "welcome", label: "Welcome", short: "W" },
  { id: "topics", label: "Topics", short: "T" },
  { id: "archive", label: "Archive", short: "A" },
  { id: "docs", label: "Fleet Docs", short: "D" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("welcome");
  const [busy, setBusy] = useState(false);

  // Welcome
  const [welcome, setWelcome] = useState<{ topic: Topic | null; total_topics: number }>({
    topic: null,
    total_topics: 0,
  });

  // Topics
  const [categories, setCategories] = useState<Category[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedCat, setSelectedCat] = useState<string>("");
  const [randomTopic, setRandomTopic] = useState<Topic | null>(null);

  // Archive
  const [archiveEntries, setArchiveEntries] = useState<ArchiveEntry[]>([]);
  const [archiveTag, setArchiveTag] = useState("");
  const [archiveForm, setArchiveForm] = useState({ topic: "", response: "", tags: "" });

  // Docs
  const [docsQuery, setDocsQuery] = useState("");
  const [docsResults, setDocsResults] = useState<DocsResult[]>([]);
  const [docsMessage, setDocsMessage] = useState("");

  // ── Welcome ──

  const loadWelcome = useCallback(async () => {
    setBusy(true);
    try {
      const r = await fetch("/api/welcome");
      const data = await r.json();
      setWelcome({ topic: data.topic, total_topics: data.total_topics });
    } catch {
      /* ignore */
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    loadWelcome();
  }, [loadWelcome]);

  // ── Topics ──

  const loadTopics = useCallback(
    async (category?: string) => {
      setBusy(true);
      try {
        const params = new URLSearchParams();
        if (category) params.set("category", category);
        const r = await fetch(`/api/topics?${params}`);
        const data = await r.json();
        setCategories(data.categories || []);
        setTopics(data.topics || []);
        setRandomTopic(null);
      } catch {
        /* ignore */
      } finally {
        setBusy(false);
      }
    },
    [],
  );

  const loadRandom = useCallback(async () => {
    setBusy(true);
    try {
      const r = await fetch("/api/topics?random=true");
      const data = await r.json();
      if (data.topics?.length) setRandomTopic(data.topics[0]);
    } catch {
      /* ignore */
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (tab === "topics") loadTopics();
  }, [tab, loadTopics]);

  // ── Archive ──

  const loadArchive = useCallback(async (tag?: string) => {
    setBusy(true);
    try {
      const params = new URLSearchParams();
      if (tag) params.set("tag", tag);
      const r = await fetch(`/api/archive?${params}`);
      const data = await r.json();
      setArchiveEntries(data.entries || []);
    } catch {
      /* ignore */
    } finally {
      setBusy(false);
    }
  }, []);

  const addArchiveEntry = useCallback(async () => {
    const tags = archiveForm.tags
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    if (!archiveForm.topic.trim() || !archiveForm.response.trim()) return;
    setBusy(true);
    try {
      await fetch("/api/archive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...archiveForm, tags }),
      });
      setArchiveForm({ topic: "", response: "", tags: "" });
      await loadArchive(archiveTag || undefined);
    } catch {
      /* ignore */
    } finally {
      setBusy(false);
    }
  }, [archiveForm, archiveTag, loadArchive]);

  const deleteArchiveEntry = useCallback(
    async (id: string) => {
      setBusy(true);
      try {
        await fetch(`/api/archive/${id}`, { method: "DELETE" });
        await loadArchive(archiveTag || undefined);
      } catch {
        /* ignore */
      } finally {
        setBusy(false);
      }
    },
    [archiveTag, loadArchive],
  );

  useEffect(() => {
    if (tab === "archive") loadArchive();
  }, [tab, loadArchive]);

  // ── Docs Search ──

  const searchDocs = useCallback(async () => {
    if (!docsQuery.trim()) return;
    setBusy(true);
    setDocsMessage("");
    try {
      const r = await fetch(`/api/docs/search?query=${encodeURIComponent(docsQuery)}&limit=5`);
      const data = await r.json();
      if (data.success) {
        setDocsResults(data.data || []);
        setDocsMessage(data.message || "");
      } else {
        setDocsResults([]);
        setDocsMessage(data.message || "Search failed");
      }
    } catch {
      setDocsMessage("Search unavailable — is docsops running?");
    } finally {
      setBusy(false);
    }
  }, [docsQuery]);

  // ── Render ──

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      {/* Header */}
      <header
        style={{
          padding: "16px 24px",
          borderBottom: "1px solid #2a2d35",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <h1 style={{ margin: 0, fontSize: 26, fontWeight: 700 }}>Chitchat</h1>
        <span style={{ color: "#6b7280", fontSize: 15 }}>v0.1.0</span>
        <span style={{ color: "#4b5563", fontSize: 15 }}>
          {welcome.total_topics} topics loaded
        </span>
      </header>

      {/* Nav */}
      <nav
        style={{
          display: "flex",
          gap: 1,
          padding: "0 24px",
          borderBottom: "1px solid #2a2d35",
          background: "#16181d",
        }}
      >
        {NAV.map((n) => (
          <button
            key={n.id}
            onClick={() => setTab(n.id)}
            style={{
              padding: "10px 16px",
              border: "none",
              background: tab === n.id ? "#1e2130" : "transparent",
              color: tab === n.id ? "#e8eaef" : "#6b7280",
              cursor: "pointer",
              fontSize: 17,
              fontFamily: "inherit",
              borderBottom: tab === n.id ? "2px solid #7ab8ff" : "2px solid transparent",
              marginBottom: -1,
            }}
          >
            {n.label}
          </button>
        ))}
        {busy && (
          <span style={{ marginLeft: "auto", alignSelf: "center", color: "#6b7280", fontSize: 15 }}>
            Loading...
          </span>
        )}
      </nav>

      {/* Content */}
      <main style={{ flex: 1, padding: 24, maxWidth: 860, width: "100%", margin: "0 auto" }}>
        {/* Welcome */}
        {tab === "welcome" && (
          <div>
            <div
              style={{
                background: "#16181d",
                borderRadius: 8,
                padding: 24,
                marginBottom: 24,
                border: "1px solid #2a2d35",
              }}
            >
              <h2 style={{ margin: "0 0 8px", fontSize: 21 }}>
                Hey! Ready for a chitchat?
              </h2>
              <p style={{ color: "#9ca3af", margin: 0 }}>
                Browse {welcome.total_topics} conversation starters across 8 categories,
                save your best chats to the archive, or search the fleet docs.
              </p>
            </div>

            {welcome.topic && (
              <div
                style={{
                  background: "linear-gradient(135deg, #1a1f3a, #1e2130)",
                  borderRadius: 8,
                  padding: 32,
                  border: "1px solid #2d3560",
                  textAlign: "center",
                }}
              >
                <div style={{ fontSize: 48, marginBottom: 12 }}>
                  {welcome.topic.emoji}
                </div>
            <div style={{ color: "#9ca3af", fontSize: 15, marginBottom: 8 }}>
              {welcome.topic.category}
            </div>
                <div style={{ fontSize: 28, fontWeight: 600, lineHeight: 1.4 }}>
                  {welcome.topic.topic}
                </div>
                <button
                  onClick={loadWelcome}
                  style={{
                    marginTop: 20,
                    padding: "8px 20px",
                    borderRadius: 6,
                    border: "1px solid #3b4290",
                    background: "transparent",
                    color: "#a8b4ff",
                    cursor: "pointer",
                    fontSize: 17,
                    fontFamily: "inherit",
                  }}
                >
                  Another one
                </button>
              </div>
            )}
          </div>
        )}

        {/* Topics */}
        {tab === "topics" && (
          <div>
            <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
              <button
                onClick={() => {
                  setSelectedCat("");
                  loadTopics();
                }}
                style={{
                  padding: "6px 14px",
                  borderRadius: 20,
                  border: `1px solid ${!selectedCat ? "#7ab8ff" : "#2a2d35"}`,
                  background: !selectedCat ? "#1a2540" : "transparent",
                  color: !selectedCat ? "#7ab8ff" : "#9ca3af",
                  cursor: "pointer",
              fontSize: 16,
              fontFamily: "inherit",
            }}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c.name}
              onClick={() => {
                setSelectedCat(c.name);
                loadTopics(c.name);
              }}
              style={{
                padding: "6px 14px",
                borderRadius: 20,
                border: `1px solid ${selectedCat === c.name ? "#7ab8ff" : "#2a2d35"}`,
                background: selectedCat === c.name ? "#1a2540" : "transparent",
                color: selectedCat === c.name ? "#7ab8ff" : "#9ca3af",
                cursor: "pointer",
                fontSize: 16,
                    fontFamily: "inherit",
                  }}
                >
                  {c.emoji} {c.name}
                </button>
              ))}
          <button
            onClick={loadRandom}
            style={{
              padding: "6px 14px",
              borderRadius: 20,
              border: "1px solid #4a5568",
              background: "transparent",
              color: "#a0aec0",
              cursor: "pointer",
              fontSize: 16,
                  fontFamily: "inherit",
                  marginLeft: "auto",
                }}
              >
                Random
              </button>
            </div>

            {randomTopic && (
              <div
                style={{
                  background: "#16181d",
                  borderRadius: 8,
                  padding: 20,
                  marginBottom: 20,
                  border: "1px solid #2d3560",
                  textAlign: "center",
                }}
              >
                <span style={{ fontSize: 28 }}>{randomTopic.emoji}</span>
                <div style={{ fontSize: 21, fontWeight: 600, marginTop: 8 }}>
                  {randomTopic.topic}
                </div>
            <div style={{ color: "#6b7280", fontSize: 15, marginTop: 4 }}>
              {randomTopic.category}
            </div>
              </div>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {topics.map((t, i) => (
                <div
                  key={i}
                  style={{
                    padding: "14px 18px",
                    background: "#16181d",
                    borderRadius: 8,
                    border: "1px solid #2a2d35",
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                  }}
                >
                  <span style={{ fontSize: 21 }}>{t.emoji}</span>
                  <span style={{ flex: 1, fontSize: 21 }}>{t.topic}</span>
                  <span style={{ color: "#6b7280", fontSize: 17 }}>{t.category}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Archive */}
        {tab === "archive" && (
          <div>
            <div
              style={{
                background: "#16181d",
                borderRadius: 8,
                padding: 20,
                marginBottom: 20,
                border: "1px solid #2a2d35",
              }}
            >
              <h3 style={{ margin: "0 0 12px", fontSize: 19 }}>Save a chat</h3>
              <input
                placeholder="Topic / question..."
                value={archiveForm.topic}
                onChange={(e) =>
                  setArchiveForm((f) => ({ ...f, topic: e.target.value }))
                }
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  marginBottom: 8,
                  background: "#0f1115",
                  border: "1px solid #2a2d35",
                  borderRadius: 6,
                  color: "#e8eaef",
                  fontSize: 17,
                  fontFamily: "inherit",
                }}
              />
              <textarea
                placeholder="Your response / notes..."
                value={archiveForm.response}
                onChange={(e) =>
                  setArchiveForm((f) => ({ ...f, response: e.target.value }))
                }
                rows={3}
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  marginBottom: 8,
                  background: "#0f1115",
                  border: "1px solid #2a2d35",
                  borderRadius: 6,
                  color: "#e8eaef",
                  fontSize: 17,
                  fontFamily: "inherit",
                  resize: "vertical",
                }}
              />
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <input
                  placeholder="Tags (comma-separated)"
                  value={archiveForm.tags}
                  onChange={(e) =>
                    setArchiveForm((f) => ({ ...f, tags: e.target.value }))
                  }
                  style={{
                    flex: 1,
                    padding: "8px 12px",
                    background: "#0f1115",
                    border: "1px solid #2a2d35",
                    borderRadius: 6,
                    color: "#e8eaef",
                    fontSize: 17,
                    fontFamily: "inherit",
                  }}
                />
                <button
                  onClick={addArchiveEntry}
                  style={{
                    padding: "8px 20px",
                    borderRadius: 6,
                    border: "none",
                    background: "#2563eb",
                    color: "#fff",
                    cursor: "pointer",
                    fontSize: 17,
                    fontFamily: "inherit",
                    fontWeight: 600,
                  }}
                >
                  Save
                </button>
              </div>
            </div>

            <div style={{ display: "flex", gap: 8, marginBottom: 16, alignItems: "center" }}>
              <input
                placeholder="Filter by tag..."
                value={archiveTag}
                onChange={(e) => {
                  setArchiveTag(e.target.value);
                  loadArchive(e.target.value || undefined);
                }}
                style={{
                  padding: "8px 12px",
                  background: "#0f1115",
                  border: "1px solid #2a2d35",
                  borderRadius: 6,
                  color: "#e8eaef",
                  fontSize: 17,
                  fontFamily: "inherit",
                  width: 200,
                }}
              />
          <span style={{ color: "#6b7280", fontSize: 17 }}>
            {archiveEntries.length} entries
          </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {archiveEntries.map((e) => (
                <div
                  key={e.id}
                  style={{
                    padding: "14px 18px",
                    background: "#16181d",
                    borderRadius: 8,
                    border: "1px solid #2a2d35",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <strong style={{ fontSize: 21 }}>{e.topic}</strong>
              <button
                  onClick={() => deleteArchiveEntry(e.id)}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "#ef4444",
                    cursor: "pointer",
                    fontSize: 15,
                        fontFamily: "inherit",
                      }}
                    >
                      Delete
                    </button>
                  </div>
                  <div style={{ color: "#9ca3af", fontSize: 17, marginBottom: 8 }}>
                    {e.response}
                  </div>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    {e.tags.map((t) => (
                      <span
                        key={t}
                        style={{
                          padding: "2px 8px",
                          background: "#1e2130",
                          borderRadius: 4,
                          fontSize: 17,
                          color: "#7ab8ff",
                        }}
                      >
                        {t}
                      </span>
                    ))}
                    <span style={{ color: "#4b5563", fontSize: 17, marginLeft: "auto" }}>
                      {new Date(e.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
              {archiveEntries.length === 0 && !busy && (
                <div style={{ color: "#6b7280", textAlign: "center", padding: 40 }}>
                  Nothing archived yet. Save a chat above!
                </div>
              )}
            </div>
          </div>
        )}

        {/* Fleet Docs */}
        {tab === "docs" && (
          <div>
            <div
              style={{
                background: "#16181d",
                borderRadius: 8,
                padding: 20,
                marginBottom: 20,
                border: "1px solid #2a2d35",
              }}
            >
              <h3 style={{ margin: "0 0 4px", fontSize: 19 }}>
                Search Fleet Documentation
              </h3>
          <p style={{ color: "#6b7280", fontSize: 15, margin: "0 0 12px" }}>
            Semantic search across mcp-central-docs — standards, patterns, port registries
          </p>
              <div style={{ display: "flex", gap: 8 }}>
                <input
                  placeholder='e.g. "FastMCP portmanteau pattern"...'
                  value={docsQuery}
                  onChange={(e) => setDocsQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") searchDocs();
                  }}
                  style={{
                    flex: 1,
                    padding: "8px 12px",
                    background: "#0f1115",
                    border: "1px solid #2a2d35",
                    borderRadius: 6,
                    color: "#e8eaef",
                    fontSize: 17,
                    fontFamily: "inherit",
                  }}
                />
                <button
                  onClick={searchDocs}
                  style={{
                    padding: "8px 20px",
                    borderRadius: 6,
                    border: "none",
                    background: "#2563eb",
                    color: "#fff",
                    cursor: "pointer",
                    fontSize: 17,
                    fontFamily: "inherit",
                    fontWeight: 600,
                  }}
                >
                  Search
                </button>
              </div>
            </div>

            {docsMessage && (
              <div
                style={{
                  padding: "10px 16px",
                  borderRadius: 6,
                  marginBottom: 16,
                  background: docsResults.length ? "#0f2a1a" : "#2a1a1a",
                  border: `1px solid ${docsResults.length ? "#1a4a2a" : "#4a2a2a"}`,
                  fontSize: 15,
                  color: "#9ca3af",
                }}
              >
                {docsMessage}
              </div>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {docsResults.map((r, i) => (
                <div
                  key={i}
                  style={{
                    padding: "14px 18px",
                    background: "#16181d",
                    borderRadius: 8,
                    border: "1px solid #2a2d35",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    {r.relative_path && (
                      <span style={{ color: "#7ab8ff", fontSize: 21 }}>{r.relative_path}</span>
                    )}
                    <span style={{ color: "#4b5563", fontSize: 17 }}>
                      Score: {(r.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div style={{ color: "#9ca3af", fontSize: 17, lineHeight: 1.5 }}>
                    {r.content.slice(0, 400)}
                    {r.content.length > 400 ? "..." : ""}
                  </div>
                </div>
              ))}
              {docsResults.length === 0 && !busy && (
                <div style={{ color: "#6b7280", textAlign: "center", padding: 40 }}>
                  Search mcp-central-docs standards, patterns, and fleet knowledge
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer
        style={{
          padding: "12px 24px",
          borderTop: "1px solid #2a2d35",
          color: "#4b5563",
          fontSize: 17,
          textAlign: "center",
        }}
      >
        Chitchat v0.1.0 — Ports 10966/10967 — Fleet docs crosslink via docsops
      </footer>
      <FloatingChat />
    </div>
  );
}
