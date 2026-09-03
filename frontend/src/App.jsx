import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");

  const checkBackend = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/");
      const data = await response.json();

      setMessage(data.message);
    } catch (error) {
      setMessage("Backend connection failed 😭");
    }
  };

  return (
    <div>
      <h1>🥯 Uzhunnuvada Battle</h1>

      <button onClick={checkBackend}>
        Test Backend Connection
      </button>

      <h2>{message}</h2>
    </div>
  );
}

export default App;
