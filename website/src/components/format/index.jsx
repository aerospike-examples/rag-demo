import React, { useEffect, useState } from "react";
import styles from "./index.module.css";
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkDirective from 'remark-directive';
import remarkGfm from 'remark-gfm';
import * as prismRenderer from 'prism-react-renderer';

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

const Format = ({className, children}) => {
    const { Highlight, themes } = prismRenderer;
    const [langsLoaded, setLangsLoaded] = useState(false);

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
            a: (props) => (
                <a href={props.href} target="_blank" rel="noopener noreferrer">{props.children}</a>
            ),
            pre: (props) => {
                const {children} = props;
                const match = /language-(\w+)/.exec(children.props.className || '');
                const code = String(children.props.children).replace(/\n$/, '');
                return (
                    langsLoaded &&
                    <Highlight language={match ? match[1] : 'asciidoc'} theme={themes.shadesOfPurple} code={code} >
                        {({ style, tokens, getLineProps, getTokenProps }) => (
                            <pre style={style} className={styles.codeBlock}>
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
                            </pre>
                        )}
                    </Highlight>
                )
            }
        }}
        remarkPlugins={[remarkGfm, remarkDirective]}
        rehypePlugins={[rehypeRaw]} />
    )
}

export default Format;