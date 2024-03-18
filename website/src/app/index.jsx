import { useEffect, useRef, useState } from 'react';
import styles from './index.module.css';
import Format from '../components/format';

function App() {
  const [prompt, setPrompt] = useState("");
  const [conversation, setConversation] = useState(null);
  const prmtRef = useRef();
  const convRef = useRef();

  useEffect(() => {
    convRef.current?.scrollIntoView({ behavior: "smooth"});
  }, [conversation])
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    let body = new FormData();
    body.append("text", prompt);

    setConversation(prev => prev === null ? `**${prompt.trim()}**\n\n` : `${prev}**${prompt.trim()}**\n\n`);
    setPrompt("");

    fetch("/rest/v1/chat", {
      method: "POST",
      body
    })
    .then(async (response) => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if(done) {
            setConversation(prev => `${prev}\n\n`);
            return
          }
          else {
            setConversation(prev => prev + decoder.decode(value, {stream: true}));
          }
        }
    })
  }

  return (
      <div className={styles.app}>
        {conversation &&
        <div className={styles.conversation}>
          <Format>{conversation}</Format>
          <div ref={convRef} />
        </div>}
        <form onSubmit={handleSubmit} className={styles.form}>
          <label>
            {!conversation && <span>Start the conversation...</span>}
            <input ref={prmtRef} type="text" value={prompt} onChange={(e) => setPrompt(e.currentTarget.value)} className={styles.prompt}/>
          </label>
          <button type="submit">&#9166;</button>
        </form>
      </div>
  )
}

export default App
