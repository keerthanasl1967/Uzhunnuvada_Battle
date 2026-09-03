import { useState } from "react";
import "./App.css";

function App() {
  const [vada1, setVada1] = useState(null);
  const [vada2, setVada2] = useState(null);
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const startBattle = async () => {

  if (!vada1 || !vada2) {
    alert("Please upload both vadas first! 🥯");
    return;
  }

  

    setChecking(true);
    setResult(null);
    setError("");

    try {
      // Create form data
     const formData = new FormData();

formData.append("vada1", vada1);
formData.append("vada2", vada2);



console.log("📤 Sending vadas to backend...");

const response = await fetch(
        "http://127.0.0.1:8000/compare",
        {
          method: "POST",
          body: formData,
        }
      );

      // Check if backend returned an error
      if (!response.ok) {
        throw new Error("Backend could not analyze the vadas.");
      }

     const data = await response.json();

alert(JSON.stringify(data));

console.log("🏆 Battle result:", data);

setResult(data);

      console.log("Backend result:", data);

      // Save real backend result
      setResult(data);
    } catch (error) {
      console.error(error);
      setError(
        "😭 Something went wrong while judging the vadas. Check that the backend is running."
      );
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="app">

      {/* HERO */}
      <header className="hero">
        <div className="badge">
          🤖 AI-POWERED • 100% UNNECESSARY
        </div>

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

          <p>
            Upload two vadas and let our extremely serious AI judge them.
          </p>
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

              {vada1 ? (
                <img
                  src={URL.createObjectURL(vada1)}
                  alt="Vada 1"
                  className="vada-image"
                />
              ) : (
                <>
                  <span className="upload-icon">📸</span>

                  <span className="upload-title">
                    Upload Vada
                  </span>

                  <span className="upload-subtitle">
                    Click here to choose an image
                  </span>
                </>
              )}

              <input
                type="file"
                accept="image/*"
                onChange={(event) => {
                  setVada1(event.target.files[0]);
                  setResult(null);
                  setError("");
                }}
              />

            </label>

            {vada1 && (
              <div className="file-name">
                📎 {vada1.name}
              </div>
            )}

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

              {vada2 ? (
                <img
                  src={URL.createObjectURL(vada2)}
                  alt="Vada 2"
                  className="vada-image"
                />
              ) : (
                <>
                  <span className="upload-icon">📸</span>

                  <span className="upload-title">
                    Upload Vada
                  </span>

                  <span className="upload-subtitle">
                    Click here to choose an image
                  </span>
                </>
              )}

              <input
                type="file"
                accept="image/*"
                onChange={(event) => {
                  setVada2(event.target.files[0]);
                  setResult(null);
                  setError("");
                }}
              />

            </label>

            {vada2 && (
              <div className="file-name">
                📎 {vada2.name}
              </div>
            )}

          </div>

        </div>


        {/* BATTLE BUTTON */}
        <div className="battle-button-container">

          <button
            className="battle-button"
            onClick={startBattle}
            disabled={checking}
          >
            {checking
              ? "🔍 JUDGING..."
              : "⚔️ START THE BATTLE"}
          </button>

          <p className="tiny-note">
            Warning: The Vada Court takes this very seriously.
          </p>

        </div>


        {/* LOADING */}
        {checking && (
          <div className="loading-card">

            <div className="spinner">🥯</div>

            <h2>
              🔍 Vada Court is investigating...
            </h2>

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

              <span>
                📊 ANALYSIS COMPLETE
              </span>

              <h2>
                ⚔️ Vada Battle Results
              </h2>

              <p>
                The Vada Court has completed its investigation.
              </p>

            </div>


            <div className="results-grid">

              {/* VADA 1 RESULT */}
              <div
                className={`result-card ${
                  result.battle.winner === "vada1"
                    ? "winner-card"
                    : ""
                }`}
              >

                {result.battle.winner === "vada1" && (
                  <div className="winner-label">
                    🏆 WINNER
                  </div>
                )}

                <h3>🥯 Vada One</h3>


                <div className="authentic">

                  <span>✅</span>

                  <div>
                    <strong>
                      Vada Analysis Complete
                    </strong>

                    <small>
                      {result.vada1.comment}
                    </small>
                  </div>

                </div>


                <Stat
                  name="⭕ Circularity"
                  value={result.vada1.stats.circularity}
                />

                <Stat
                  name="⚖️ Symmetry"
                  value={result.vada1.stats.symmetry}
                />

                <Stat
                  name="🕳️ Hole Quality"
                  value={result.vada1.stats.holeQuality}
                />

                <Stat
                  name="🔥 Crispiness"
                  value={result.vada1.stats.crispiness}
                />


                <div className="iq-box">

                  <span>🧠 VADA IQ</span>

                  <strong>
                    {result.vada1.stats.vadaIQ}
                  </strong>

                </div>

              </div>


              {/* VADA 2 RESULT */}
              <div
                className={`result-card ${
                  result.battle.winner === "vada2"
                    ? "winner-card"
                    : ""
                }`}
              >

                {result.battle.winner === "vada2" && (
                  <div className="winner-label">
                    🏆 WINNER
                  </div>
                )}

                <h3>🥯 Vada Two</h3>


                <div className="authentic">

                  <span>✅</span>

                  <div>
                    <strong>
                      Vada Analysis Complete
                    </strong>

                    <small>
                      {result.vada2.comment}
                    </small>
                  </div>

                </div>


                <Stat
                  name="⭕ Circularity"
                  value={result.vada2.stats.circularity}
                />

                <Stat
                  name="⚖️ Symmetry"
                  value={result.vada2.stats.symmetry}
                />

                <Stat
                  name="🕳️ Hole Quality"
                  value={result.vada2.stats.holeQuality}
                />

                <Stat
                  name="🔥 Crispiness"
                  value={result.vada2.stats.crispiness}
                />


                <div className="iq-box">

                  <span>🧠 VADA IQ</span>

                  <strong>
                    {result.vada2.stats.vadaIQ}
                  </strong>

                </div>

              </div>

            </div>


            {/* FINAL WINNER */}
            <div className="final-winner">

              <div className="trophy">
                🏆
              </div>

              <p>
                THE VADA COURT HAS SPOKEN
              </p>


              {result.battle.winner === "vada1" && (
                <h1>
                  VADA ONE WINS!
                </h1>
              )}

              {result.battle.winner === "vada2" && (
                <h1>
                  VADA TWO WINS!
                </h1>
              )}

              {result.battle.winner === "draw" && (
                <h1>
                  IT'S A DRAW!
                </h1>
              )}


              <span>
                {result.battle.message}
              </span>


              <div className="difference">
                📊 Vada IQ Difference:{" "}
                <strong>
                  {result.battle.difference}
                </strong>
              </div>

            </div>

          </section>
        )}

      </main>


      {/* FOOTER */}
      <footer>
        <p>
          🥯 Built with React • Powered by questionable AI decisions
        </p>
      </footer>

    </div>
  );
}


/* STAT COMPONENT */
function Stat({ name, value }) {

  return (
    <div className="stat">

      <div className="stat-top">

        <span>
          {name}
        </span>

        <strong>
          {Number(value).toFixed(2)}%
        </strong>

      </div>

      <div className="progress">

        <div
          className="progress-fill"
          style={{
            width: `${value}%`,
          }}
        />

      </div>

    </div>
  );
}


export default App;
