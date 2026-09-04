import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [vada1, setVada1] = useState(null);
  const [vada2, setVada2] = useState(null);
  const [preview1, setPreview1] = useState(null);
  const [preview2, setPreview2] = useState(null);
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // Handle preview URLs cleanly to prevent memory leaks
  useEffect(() => {
    if (!vada1) {
      setPreview1(null);
      return;
    }
    const url = URL.createObjectURL(vada1);
    setPreview1(url);
    return () => URL.revokeObjectURL(url);
  }, [vada1]);

  useEffect(() => {
    if (!vada2) {
      setPreview2(null);
      return;
    }
    const url = URL.createObjectURL(vada2);
    setPreview2(url);
    return () => URL.revokeObjectURL(url);
  }, [vada2]);

  const startBattle = async () => {
    if (!vada1 || !vada2) {
      alert("Please upload both vadas first! 🥯");
      return;
    }

    setChecking(true);
    setResult(null);
    setError("");

    try {
      const formData = new FormData();
      formData.append("vada1", vada1);
      formData.append("vada2", vada2);

      const response = await fetch("http://127.0.0.1:8000/compare", {
        method: "POST",
        body: formData,
      });

      console.log("Status:", response.status);

const data = await response.json();

console.log(JSON.stringify(data, null, 2));

if (!response.ok) {
  throw new Error(data.detail || "Backend error");
}

setResult(data);
    } catch (err) {
  console.error("ACTUAL ERROR:", err);

  alert(err.message);

  setError(err.message);
} finally {
      setChecking(false);
    }
  };

  const downloadCertificate = () => {
  if (!result || result.battle.winner === "tie") return;

  const winner =
    result.battle.winner === "vada1"
      ? result.vada1
      : result.vada2;

  const winnerName =
    result.battle.winner === "vada1"
      ? "Vada One"
      : "Vada Two";

  const stats = winner.opencv?.stats || {};

  const certificateWindow = window.open("", "_blank");

  if (!certificateWindow) {
    alert("Popup blocked! Please allow popups to print the certificate.");
    return;
  }

  certificateWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Excellent Vada Certificate</title>

      <style>
        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          padding: 25px;
          background: #f7efd8;
          font-family: "Comic Sans MS", "Trebuchet MS", cursive;
        }

        .certificate {
          width: 1100px;
          min-height: 750px;
          margin: auto;
          padding: 35px 50px;
          background: #fff8e8;
          border: 7px solid #1c1c1c;
          position: relative;
          text-align: center;
        }

        .certificate-title {
          font-size: 72px;
          font-weight: 900;
          letter-spacing: 6px;
          margin: 0;
        }

        .of {
          font-size: 32px;
          font-weight: bold;
          margin-top: -10px;
        }

        .ribbon {
          display: inline-block;
          background: #f4b91c;
          border: 5px solid #111;
          padding: 15px 55px;
          font-size: 42px;
          font-weight: 900;
          letter-spacing: 5px;
          margin: 10px 0 25px;
          transform: rotate(-1deg);
        }

        .presented {
          font-size: 25px;
          margin: 0 0 10px;
        }

        .winner-name {
          width: 60%;
          margin: 15px auto 30px;
          padding: 10px;
          border-bottom: 4px solid #111;
          font-size: 38px;
          font-weight: bold;
        }

        .middle {
          display: grid;
          grid-template-columns: 260px 1fr 270px;
          align-items: center;
          gap: 25px;
          margin-top: 20px;
        }

        .seal {
          width: 210px;
          height: 210px;
          margin: auto;
          border-radius: 50%;
          background: #f4b91c;
          border: 6px solid #111;
          display: flex;
          align-items: center;
          justify-content: center;
          text-align: center;
          font-weight: 900;
          font-size: 26px;
          line-height: 1.1;
          padding: 20px;
        }

        .vada-area {
          text-align: center;
        }

        .vada {
          width: 230px;
          height: 230px;
          margin: auto;
          background: #d78224;
          border: 6px solid #111;
          border-radius: 50%;
          position: relative;
          box-shadow: inset 0 0 0 12px rgba(255,255,255,.08);
        }

        .vada-hole {
          width: 65px;
          height: 65px;
          border-radius: 50%;
          background: #fff8e8;
          border: 5px solid #111;
          position: absolute;
          top: 82px;
          left: 78px;
        }

        .eyes {
          position: absolute;
          top: 62px;
          width: 100%;
          display: flex;
          justify-content: center;
          gap: 75px;
          font-size: 28px;
          font-weight: bold;
        }

        .mouth {
          position: absolute;
          top: 140px;
          left: 82px;
          font-size: 48px;
        }

        .speech {
          margin: 18px auto 0;
          max-width: 360px;
          padding: 18px;
          border: 4px solid #111;
          border-radius: 30px;
          background: white;
          font-size: 22px;
        }

        .details {
          border: 4px solid #111;
          border-radius: 22px;
          padding: 20px;
          text-align: left;
          font-size: 21px;
          background: #fffdf4;
        }

        .details h3 {
          text-align: center;
          font-size: 28px;
          margin: 0 0 15px;
          text-decoration: underline;
        }

        .details-row {
          display: flex;
          justify-content: space-between;
          margin: 12px 0;
        }

        .bottom-message {
          font-size: 27px;
          margin-top: 30px;
          font-weight: bold;
        }

        .bottom-row {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          margin-top: 35px;
          font-size: 21px;
        }

        .signature {
          width: 220px;
          border-top: 3px solid #111;
          padding-top: 8px;
          text-align: center;
          font-weight: bold;
        }

        @media print {
          body {
            background: white;
            padding: 0;
          }

          .certificate {
            transform: scale(.86);
            transform-origin: top left;
          }
        }
      </style>
    </head>

    <body>
      <div class="certificate">

        <h1 class="certificate-title">CERTIFICATE</h1>
        <div class="of">OF</div>

        <div class="ribbon">
          EXCELLENT VADA
        </div>

        <p class="presented">
          Proudly presented to
        </p>

        <div class="winner-name">
          ${winnerName}
        </div>

        <div class="middle">

          <div class="seal">
            👑<br>
            OFFICIAL<br>
            VADA<br>
            APPROVED
          </div>

          <div class="vada-area">

            <div class="vada">
              <div class="eyes">
                <span>⌒</span>
                <span>⌒</span>
              </div>

              <div class="vada-hole"></div>

              <div class="mouth">
                😄
              </div>
            </div>

            <div class="speech">
              I may have just 1 hole,<br>
              but I'm 100% AWESOME!
            </div>

          </div>

          <div class="details">

            <h3>DETAILS</h3>

            <div class="details-row">
              <span>Circularity</span>
              <strong>${stats.circularity ?? "N/A"}%</strong>
            </div>

            <div class="details-row">
              <span>Symmetry</span>
              <strong>${stats.symmetry ?? "N/A"}%</strong>
            </div>

            <div class="details-row">
              <span>Hole Quality</span>
              <strong>${stats.holeQuality ?? "N/A"}%</strong>
            </div>

            <div class="details-row">
              <span>Crispiness</span>
              <strong>${stats.crispiness ?? "N/A"}%</strong>
            </div>

            <div class="details-row">
              <span>Vada IQ</span>
              <strong>${stats.vadaIQ ?? "N/A"}</strong>
            </div>

          </div>

        </div>

        <div class="bottom-message">
          Thank you for being the best vada ever! ❤️
        </div>

        <div class="bottom-row">

          <div>
            Date:
            <strong>${new Date().toLocaleDateString()}</strong>
          </div>

          <div class="signature">
            👑<br>
            VADA JUDGE
          </div>

        </div>

      </div>

      <script>
        window.onload = function () {
          window.print();
        };
      </script>

    </body>
    </html>
  `);

  certificateWindow.document.close();
};

  return (
    <div className="app">
      {/* HERO */}
      <header className="hero">
        <div className="badge">🤖 AI-POWERED • 100% UNNECESSARY</div>
        <h1>🥯 Uzhunnuvada Battle</h1>
        <p>
          Two vadas enter.
          <br />
          Only one leaves as the <strong>Ultimate Vada.</strong>
        </p>
      </header>

      {/* MAIN */}
      <main className="battle-container">
        <div className="section-title">
          <h2>⚔️ Choose Your Vadas</h2>
          <p>Upload two vadas and let our extremely serious AI judge them.</p>
        </div>

        {/* TWO VADA UPLOADS */}
        <div className="vada-arena">
          {/* VADA 1 */}
          <div className="vada-card">
            <div className="card-header">
              <span className="player-number">01</span>
              <h3>Vada One</h3>
            </div>

            <label className="upload-box">
              {preview1 ? (
                <img src={preview1} alt="Vada 1" className="vada-image" />
              ) : (
                <>
                  <span className="upload-icon">📸</span>
                  <span className="upload-title">Upload Vada</span>
                  <span className="upload-subtitle">Click here to choose an image</span>
                </>
              )}

              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  setVada1(e.target.files[0] || null);
                  setResult(null);
                  setError("");
                }}
              />
            </label>

            {vada1 && <div className="file-name">📎 {vada1.name}</div>}
          </div>

          {/* VS */}
          <div className="vs-container">
            <div className="vs-circle">VS</div>
            <span>🥊</span>
          </div>

          {/* VADA 2 */}
          <div className="vada-card">
            <div className="card-header">
              <span className="player-number">02</span>
              <h3>Vada Two</h3>
            </div>

            <label className="upload-box">
              {preview2 ? (
                <img src={preview2} alt="Vada 2" className="vada-image" />
              ) : (
                <>
                  <span className="upload-icon">📸</span>
                  <span className="upload-title">Upload Vada</span>
                  <span className="upload-subtitle">Click here to choose an image</span>
                </>
              )}

              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  setVada2(e.target.files[0] || null);
                  setResult(null);
                  setError("");
                }}
              />
            </label>

            {vada2 && <div className="file-name">📎 {vada2.name}</div>}
          </div>
        </div>

        {/* BATTLE BUTTON */}
        <div className="battle-button-container">
          <button
            className="battle-button"
            onClick={startBattle}
            disabled={checking}
          >
            {checking ? "🔍 JUDGING..." : "⚔️ START THE BATTLE"}
          </button>
          <p className="tiny-note">
            Warning: The Vada Court takes this very seriously.
          </p>
        </div>

        {/* LOADING */}
        {checking && (
          <div className="loading-card">
            <div className="spinner">🥯</div>
            <h2>🔍 Vada Court is investigating...</h2>
            <p>
              Measuring circularity...
              <br />
              Inspecting hole quality...
              <br />
              Calculating Vada IQ...
            </p>
          </div>
        )}

        {/* ERROR */}
        {error && (
          <div className="error-card">
            <h2>🚨 Vada Court Error</h2>
            <p>{error}</p>
          </div>
        )}

        {/* RESULTS */}
        {result && (
          <section className="results">
            <div className="result-heading">
              <span>📊 ANALYSIS COMPLETE</span>
              <h2>⚔️ Vada Battle Results</h2>
              <p>The Vada Court has completed its investigation.</p>
            </div>

            <div className="results-grid">
              {/* VADA 1 RESULT */}
              <div
                className={`result-card ${
                  result.battle.winner === "vada1" ? "winner-card" : ""
                }`}
              >
                {result.battle.winner === "vada1" && (
                  <div className="winner-label">🏆 WINNER</div>
                )}
                <h3>🥯 Vada One</h3>

                <div className="authentic">
                  <span>✅</span>
                  <div>
                    <strong>Vada Analysis Complete</strong>
                    <small>{result.vada1?.appearance}</small>
                  </div>
                </div>

                <Stat
                  name="⭕ Circularity"
                  value={result.vada1?.opencv?.stats?.circularity}
                />
                <Stat
                  name="⚖️ Symmetry"
                  value={result.vada1?.opencv?.stats?.symmetry}
                />
                <Stat
                  name="🕳️ Hole Quality"
                  value={result.vada1?.opencv?.stats?.holeQuality}
                />
                <Stat
                  name="🔥 Crispiness"
                  value={result.vada1?.opencv?.stats?.crispiness}
                />

                <div className="iq-box">
                  <span>🧠 VADA IQ</span>
                  <strong>{result.vada1?.opencv?.stats?.vadaIQ}</strong>
                </div>
              </div>

              {/* VADA 2 RESULT */}
              <div
                className={`result-card ${
                  result.battle.winner === "vada2" ? "winner-card" : ""
                }`}
              >
                {result.battle.winner === "vada2" && (
                  <div className="winner-label">🏆 WINNER</div>
                )}
                <h3>🥯 Vada Two</h3>

                <div className="authentic">
                  <span>✅</span>
                  <div>
                    <strong>Vada Analysis Complete</strong>
                    <small>{result.vada2?.appearance}</small>
                  </div>
                </div>

                <Stat
                  name="⭕ Circularity"
                  value={result.vada2?.opencv?.stats?.circularity}
                />
                <Stat
                  name="⚖️ Symmetry"
                  value={result.vada2?.opencv?.stats?.symmetry}
                />
                <Stat
                  name="🕳️ Hole Quality"
                  value={result.vada2?.opencv?.stats?.holeQuality}
                />
                <Stat
                  name="🔥 Crispiness"
                  value={result.vada2?.opencv?.stats?.crispiness}
                />

                <div className="iq-box">
                  <span>🧠 VADA IQ</span>
                  <strong>{result.vada2?.opencv?.stats?.vadaIQ}</strong>
                </div>
              </div>
            </div>

            {/* FINAL WINNER BANNER */}
            <div className="final-winner">
              <div className="trophy">🏆</div>
              <p>THE VADA COURT HAS SPOKEN</p>

              {result.battle.winner === "vada1" && <h1>VADA ONE WINS!</h1>}
              {result.battle.winner === "vada2" && <h1>VADA TWO WINS!</h1>}
              {result.battle.winner === "tie" && <h1>IT'S A DRAW!</h1>}

              <span>{result.battle.message}</span>

              <div className="difference">
                📊 Vada IQ Difference: <strong>{result.battle.difference}</strong>
              </div>
            </div>

            {/* WINNER CERTIFICATE (Placed outside cards, at bottom of results) */}
            {result.battle.winner !== "tie" && (
              <div className="certificate-section">
                <h2>🏅 Winner Certificate</h2>
                <div className="certificate-preview">
                  <h1>🏆 Certificate of Vada Excellence</h1>
                  <p>This certificate is proudly awarded to</p>
                  <h2>
                    {result.battle.winner === "vada1"
                      ? result.vada1.name || "Vada One"
                      : result.vada2.name || "Vada Two"}
                  </h2>
                  <p>for winning the Uzhunnuvada Battle</p>
                  <strong>
                    Final Score:{" "}
                    {result.battle.winner === "vada1"
                      ? result.vada1.finalScore ?? result.vada1.opencv?.stats?.vadaIQ
                      : result.vada2.finalScore ?? result.vada2.opencv?.stats?.vadaIQ}
                  </strong>
                  <p>🥯 The Vada Court</p>
                </div>

                <button
                  className="certificate-button"
                  onClick={downloadCertificate}
                >
                  📜 Download Certificate
                </button>
              </div>
            )}
          </section>
        )}
      </main>

      {/* FOOTER */}
      <footer>
        <p>🥯 Built with React • Powered by questionable AI decisions</p>
      </footer>
    </div>
  );
}

/* STAT COMPONENT */
function Stat({ name, value = 0 }) {
  const numericValue = Number(value) || 0;
  return (
    <div className="stat">
      <div className="stat-top">
        <span>{name}</span>
        <strong>{numericValue.toFixed(2)}%</strong>
      </div>
      <div className="progress">
        <div
          className="progress-fill"
          style={{ width: `${Math.min(Math.max(numericValue, 0), 100)}%` }}
        />
      </div>
    </div>
  );
}

export default App;