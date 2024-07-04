import { useEffect, useRef, useState } from 'react';
import styles from './index.module.css';
import Format from '../format';

const Conversation = () => {
	const [prompt, setPrompt] = useState("");
	const [conversation, setConversation] = useState(null);
	const [waiting, setWaiting] = useState(false);
	const [streaming, setStreaming] = useState(false);
	const prmtRef = useRef();
	const convRef = useRef();

	useEffect(() => {
		convRef.current?.scrollIntoView({ behavior: "smooth"});
	}, [conversation])
	
	const handleSubmit = async (e) => {
		e.preventDefault();
		if(!prompt) return;

		let body = new FormData();
		body.append("text", prompt);
		
		setStreaming(true);
		setConversation(prev => prev === null ? `### ${prompt.trim()}\n\n` : `${prev}### ${prompt.trim()}\n\n`);
		setPrompt("");

		fetch("http://localhost:8080/rest/v1/chat/", {
			method: "POST",
			body
		})
		.then(async (response) => {
			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			while (true) {
				const { done, value } = await reader.read();
				if(done) {
					setConversation(prev => `${prev}\n\n<hr />\n\n`);
					setStreaming(false);
					setTimeout(() => prmtRef.current.focus(), 100);
					return
				}
				else {
					let text = decoder.decode(value, {stream: true});
					if(text === "\nGenerating a response...\n\n" || text === "\nWaiting for slot...\n\n") setWaiting(true);
					else setWaiting(false);
					setConversation(prev => prev + text);
				}
			}
		})
	}

	return (
		<div className={styles.content}>
			<div className={styles.container}>
			{conversation &&
			<div className={styles.conversation}>
				<Format>{conversation}</Format>
				{waiting && <div className={styles.waiting}/>}
				<div ref={convRef} />
			</div>}
			<form onSubmit={handleSubmit} className={styles.form}>
				<label>
				<input ref={prmtRef} type="text" value={prompt} onChange={(e) => setPrompt(e.currentTarget.value)} className={styles.prompt} disabled={waiting || streaming} placeholder='Ask a question...' />
				</label>
				<button type="submit">&#9166;</button>
			</form>
			</div>
		</div>
	)
}

export default Conversation;
