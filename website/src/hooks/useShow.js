import { useEffect, useRef, useState } from "react";

/**
 * Hook for controlling the display of a component with event handlers 
 * for clicking outside the ref and pressing Escape. Set `danger` true
 * to remove the event handlers and force user interaction.
 * 
 * @param {boolean} [danger] - optional param to turn off event handlers.
 * @param {(() => void)} [callback] - optional callback to run after event trigger.
 * @returns {[showRef, show, setShow]} a ref to attach to a DOM element, a stateful boolean, and a function to set it.
 */
//useShow is exported
export const useShow = (danger = false, callback = () => {}) => {
    const showRef = useRef(null);
    const [show, setShow] = useState(false);

    const handleEvent = () => {
        setShow(false);
        callback();
    }
    const handleEscape = (e) => {
        if(e.code === "Escape") handleEvent();
    }
    const handleOutside = (e) => {
        if(showRef.current && !showRef.current.contains(e.target)) handleEvent();
    }

    useEffect(() => {
        if(!danger){
            window.addEventListener("keydown", handleEscape);
            window.addEventListener("mousedown", handleOutside);
            
            return () => {
                window.removeEventListener("keydown", handleEscape);
                window.removeEventListener("mousedown", handleOutside);
            }
        }
    },[danger]);

    return [ showRef, show, setShow ];
}