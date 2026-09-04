import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");

  const [indexResult, setIndexResult] = useState(null);
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [isIndexing, setIsIndexing] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState("");

  const indexRepository = async () => {
    if (!repoUrl.trim()) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    setError("");
    setIndexResult(null);
    setAnswer("");
    setSources([]);
    setIsIndexing(true);

    try {
      const response = await fetch(`${API_URL}/index`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Repository indexing failed.");
      }

      setIndexResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsIndexing(false);
    }
  };

  const askQuestion = async () => {
    if (!repoUrl.trim()) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setError("");
    setAnswer("");
    setSources([]);
    setIsAsking(true);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to generate an answer.");
      }

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-icon">&lt;/&gt;</div>
          <div>
            <h1>Codebase Assistant</h1>
            <p>Understand your GitHub repositories with AI</p>
          </div>
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <p className="eyebrow">AI-POWERED CODE EXPLORATION</p>
          <h2>Ask questions about your codebase.</h2>
          <p className="hero-text">
            Index a GitHub repository and get grounded answers with relevant
            file and line references.
          </p>
        </section>

        <section className="card">
          <label htmlFor="repoUrl">GitHub Repository URL</label>

          <div className="input-row">
            <input
              id="repoUrl"
              type="url"
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(event) => setRepoUrl(event.target.value)}
            />

            <button
              className="primary-button"
              onClick={indexRepository}
              disabled={isIndexing}
            >
              {isIndexing ? "Indexing..." : "Index Repository"}
            </button>
          </div>

          {indexResult && (
            <div className="success-box">
              <strong>Repository indexed successfully.</strong>

              <div className="stats">
                <span>
                  Files scanned: <b>{indexResult.files_scanned}</b>
                </span>
                <span>
                  Chunks stored: <b>{indexResult.chunks_stored}</b>
                </span>
              </div>
            </div>
          )}
        </section>

        <section className="card">
          <label htmlFor="question">Ask a Question</label>

          <textarea
            id="question"
            placeholder="Where is the application initialized?"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows="4"
          />

          <button
            className="primary-button ask-button"
            onClick={askQuestion}
            disabled={isAsking}
          >
            {isAsking ? "Analyzing Codebase..." : "Ask Assistant"}
          </button>
        </section>

        {error && <div className="error-box">{error}</div>}

        {answer && (
          <section className="card answer-card">
            <div className="section-heading">
              <span className="status-dot"></span>
              <h3>AI Answer</h3>
            </div>

            <div className="answer">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>  
                {answer}
              </ReactMarkdown>
            </div>

            {sources.length > 0 && (
              <div className="sources">
                <h3>Relevant Sources</h3>

                {sources.map((source, index) => (
                  <div className="source-item" key={index}>
                    <span className="source-number">{index + 1}</span>

                    <div>
                      <strong>{source.file}</strong>
                      <p>
                        Lines {source.start_line}–{source.end_line}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;