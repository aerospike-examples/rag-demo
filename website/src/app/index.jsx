import { useState } from 'react';
import styles from './index.module.css';

function App() {
  const [prompt, setPrompt] = useState("");
  const [files, setFiles] = useState([]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    let body = new FormData();
    body.append("text", prompt);

    fetch("/rest/v1/search", {
      method: "POST",
      body
    })
    .then(async (data) => {
      let results = await data.json();
      console.log(results);
    })
  }

  return (
      <div className={styles.app}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <label>
            <span>Ask a question...</span>
            <input type="text" value={prompt} onChange={(e) => setPrompt(e.currentTarget.value)} className={styles.prompt}/>
          </label>
          <button type="submit">Send</button>
        </form>
      </div>
  )
}

export default App
