import { useState } from "react";
import { useShow } from "./useShow";

//useModal is exported
export const useModal = (danger = false, modalCallback = () => {}) => {
    const [open, setOpen] = useState(false);
    
    const callback = () => {
        setTimeout(() => {
            setOpen(false);
            modalCallback();
        }, 300);
    };
    
    const [ showRef, show, setShow ] = useShow(danger, callback);

    const openModal = () => {
        setOpen(true);
        setTimeout(() => setShow(true), 100);
    }
    const closeModal = () => {
        setShow(false);
        callback();
    }

    return { modalProps: {open, show, closeModal, danger}, ref: showRef, openModal, closeModal }
}