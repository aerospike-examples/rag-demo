import React, { useEffect, useState } from "react";
import styles from "./index.module.css";
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkDirective from 'remark-directive';
import remarkGfm from 'remark-gfm';
import * as prismRenderer from 'prism-react-renderer';
import clsx from "clsx";

(typeof global !== "undefined" ? global : window).Prism = prismRenderer.Prism;

const registerLangs = async () => {
    return new Promise(async resolve => {
        await import("prismjs/components/prism-javascript");
        await import("prismjs/components/prism-java");
        await import("prismjs/components/prism-python");
        await import("prismjs/components/prism-c");
        await import("prismjs/components/prism-go");
        await import("prismjs/components/prism-csharp");
        await import("prismjs/components/prism-ruby");
        await import("prismjs/components/prism-rust");

        resolve();
    })
}

const CopyIcon = () => {
    return (
        <svg viewBox="0 0 24 24" className={styles.copyIcon} xmlns="http://www.w3.org/2000/svg">
            <path d="M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z"></path>
        </svg>
    )
}

const Copied = () => {
    return (
        <svg className={styles.copiedIcon} version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130.2 130.2">
            <polyline className={clsx(styles.path, styles.check)} fill="none" stroke="#73AF55" strokeWidth="16" strokeLinecap="round" strokeMiterlimit="10" points="100.2,40.2 51.5,88.8 29.8,67.5 "/>
        </svg>
    )
}
const Format = ({className, children}) => {
    const { Highlight, themes } = prismRenderer;
    const [langsLoaded, setLangsLoaded] = useState(false);
    const [copied, setCopied] = useState(false);

    const copyCode = (code) => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    }

    useEffect(() => {
        if(!langsLoaded) registerLangs().then(() => setLangsLoaded(true));
    }, []);

    return (
    <ReactMarkdown
        children={children}
        components={{
            p: (props) => (
                <p className={className}>{props.children}</p>
            ),
            a: (props) => {
                let href = props.href.startsWith("http") ? 
                    props.href
                    :
                    props.href.startsWith("/") ?
                        `https://aerospike.com${props.href}`
                        :
                        `https://${props.href}`;
                        
                return (
                    <a href={href} target="_blank" rel="noopener noreferrer">{props.children}</a>
                )
            },
            pre: (props) => {
                const {children} = props;
                const match = /language-(\w+)/.exec(children.props.className || '');
                const code = String(children.props.children).replace(/\n$/, '');
                return (
                    langsLoaded &&
                    <Highlight language={match ? match[1] : 'asciidoc'} theme={themes.shadesOfPurple} code={code} >
                        {({ className, style, tokens, getLineProps, getTokenProps }) => {
                            const lines = tokens.length;
                            return (
                                <pre style={style} className={styles.codeBlock}>
                                    <div className={styles.codeBlockContents}>
                                    <div className={styles.lineNumbers}>
                                        {Array.from({length: lines}).map((_, i) => <span key={i}>{i + 1}</span>)}
                                    </div>
                                    <div className={styles.codeContainer}>
                                        <div className={styles.code}>
                                            {tokens.map((line, i) => (
                                            <div key={i} {...getLineProps({ line })}>
                                                {line.map((token, key) => (
                                                <span key={key} {...getTokenProps({ token })} />
                                                ))}
                                            </div>
                                            ))}
                                        </div>
                                    </div>
                                    </div>
                                    {/*<button className={clsx(styles.copy, copied && styles.copied)} onClick={() => copyCode(code)}>{copied ? <Copied /> : <CopyIcon />}</button>*/}
                                </pre>
                            )
                        }}
                    </Highlight>
                )
            }
        }}
        remarkPlugins={[remarkGfm, remarkDirective]}
        rehypePlugins={[rehypeRaw]} />
    )
}

export default Format;