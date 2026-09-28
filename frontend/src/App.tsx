import { FormEvent, useEffect, useRef, useState } from "react";
import {
  ArrowUp,
  BookOpen,
  Bot,
  CheckCircle2,
  FileText,
  Menu,
  PanelLeftClose,
  Plus,
  Sparkles,
  Trash2,
  UploadCloud,
  User,
  X,
} from "lucide-react";
import { api, Citation, DocumentSummary } from "./api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

const welcomeMessage: Message = {
  id: "welcome",
  role: "assistant",
  content:
    "Hi, I’m Knowva. Upload company documents, then ask me anything about their content. I’ll answer from your knowledge base and show exactly where the information came from.",
};

function App() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const fileInput = useRef<HTMLInputElement>(null);
  const chatEnd = useRef<HTMLDivElement>(null);

  const refreshDocuments = async () => {
    try {
      setDocuments(await api.listDocuments());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load documents");
    }
  };

  useEffect(() => {
    void refreshDocuments();
  }, []);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const upload = async (file?: File) => {
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await api.uploadDocument(file);
      await refreshDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  };

  const removeDocument = async (id: string) => {
    setError("");
    try {
      await api.deleteDocument(id);
      setDocuments((current) => current.filter((doc) => doc.document_id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const ask = async (event: FormEvent) => {
    event.preventDefault();
    const cleanQuestion = question.trim();
    if (!cleanQuestion || loading) return;

    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", content: cleanQuestion },
    ]);
    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const result = await api.query(cleanQuestion);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: result.answer,
          citations: result.citations,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not answer the question");
    } finally {
      setLoading(false);
    }
  };

  const newChat = () => {
    setMessages([welcomeMessage]);
    setQuestion("");
    setError("");
  };

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="brand-row">
          <div className="brand-mark"><Sparkles size={20} /></div>
          <div className="brand-copy">
            <strong>Knowva</strong><span>AI</span>
          </div>
          <button className="icon-button collapse" onClick={() => setSidebarOpen(false)} aria-label="Close sidebar">
            <PanelLeftClose size={19} />
          </button>
        </div>

        <button className="new-chat" onClick={newChat}><Plus size={18} /> New conversation</button>

        <div className="sidebar-heading">
          <span>KNOWLEDGE BASE</span>
          <span className="count">{documents.length}</span>
        </div>

        <div
          className={`drop-zone ${dragging ? "dragging" : ""}`}
          onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);
            void upload(event.dataTransfer.files[0]);
          }}
          onClick={() => fileInput.current?.click()}
        >
          <input
            ref={fileInput}
            type="file"
            hidden
            accept=".pdf,.docx,.txt,.md"
            onChange={(event) => void upload(event.target.files?.[0])}
          />
          <UploadCloud size={22} />
          <strong>{uploading ? "Indexing document…" : "Upload a document"}</strong>
          <small>PDF, DOCX, TXT or MD · max 10 MB</small>
        </div>

        <div className="document-list">
          {documents.length === 0 && !uploading ? (
            <div className="empty-docs"><BookOpen size={20} /><span>Your sources will appear here</span></div>
          ) : documents.map((document) => (
            <div className="document-card" key={document.document_id}>
              <div className="file-icon"><FileText size={18} /></div>
              <div className="document-info">
                <strong title={document.filename}>{document.filename}</strong>
                <small>{document.chunks} {document.chunks === 1 ? "chunk" : "chunks"} indexed</small>
              </div>
              <button className="delete-button" onClick={() => void removeDocument(document.document_id)} aria-label={`Delete ${document.filename}`}>
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>Knowledge engine online</span>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          {!sidebarOpen && (
            <button className="icon-button" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar"><Menu size={20} /></button>
          )}
          <div>
            <h1>Company knowledge</h1>
            <p>{documents.length ? `${documents.length} ${documents.length === 1 ? "source" : "sources"} ready` : "Upload a source to begin"}</p>
          </div>
          <div className="rag-badge"><CheckCircle2 size={15} /> Source grounded</div>
        </header>

        <section className="chat-area">
          <div className="messages">
            {messages.map((message) => (
              <article className={`message ${message.role}`} key={message.id}>
                <div className="avatar">{message.role === "assistant" ? <Bot size={19} /> : <User size={18} />}</div>
                <div className="message-body">
                  <div className="message-label">{message.role === "assistant" ? "KNOWVA" : "YOU"}</div>
                  <p>{message.content}</p>
                  {!!message.citations?.length && (
                    <div className="citations">
                      <div className="citation-heading"><BookOpen size={15} /> Sources</div>
                      {message.citations.map((citation, index) => (
                        <details className="citation" key={`${citation.document_id}-${citation.chunk}-${index}`}>
                          <summary><span>[{index + 1}]</span>{citation.filename}<small>Chunk {citation.chunk}</small></summary>
                          <p>{citation.excerpt}</p>
                        </details>
                      ))}
                    </div>
                  )}
                </div>
              </article>
            ))}

            {loading && (
              <article className="message assistant">
                <div className="avatar"><Bot size={19} /></div>
                <div className="message-body"><div className="message-label">KNOWVA</div><div className="thinking"><span /><span /><span /></div></div>
              </article>
            )}
            <div ref={chatEnd} />
          </div>
        </section>

        <div className="composer-wrap">
          {error && <div className="error-banner"><span>{error}</span><button onClick={() => setError("")}><X size={16} /></button></div>}
          <form className="composer" onSubmit={(event) => void ask(event)}>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }}
              placeholder={documents.length ? "Ask a question about your company knowledge…" : "Upload a document before asking a question…"}
              rows={1}
              disabled={!documents.length || loading}
            />
            <button type="submit" className="send-button" disabled={!question.trim() || loading || !documents.length} aria-label="Send question">
              <ArrowUp size={20} />
            </button>
          </form>
          <p className="disclaimer">Knowva answers from your uploaded sources. Verify important information.</p>
        </div>
      </main>
    </div>
  );
}

export default App;
