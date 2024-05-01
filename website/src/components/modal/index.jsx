import React, { forwardRef } from "react";
import { createPortal } from "react-dom";
import styles from "./index.module.css";
import clsx from "clsx";
import { usePortal } from "../../hooks/usePortal";
import { Button } from "../buttons";

const Modal = forwardRef((props, ref) => {
    const [ portalRef ] = usePortal();
    const { open, show, closeModal, danger, title, children, buttons = undefined } = props;

    return (
        open && createPortal(
            <div className={styles.modalContainer}>
            <div className={clsx(styles.modalBackground, show && styles.modalBackgroundOpen)}/>
            <div className={clsx(styles.modalMain, show && styles.modalMainOpen)} ref={ref}>
                {!danger && <div className={styles.close} onClick={closeModal}><span>&#10005;</span></div>}
                {title && <h2 className={styles.title}>{title}</h2>}
                <div className={styles.children}>
                {children}
                </div>
                <div className={styles.controls}>
                    {typeof buttons === 'object' ? buttons.map((btn, idx) => <React.Fragment key={idx}>{btn}</React.Fragment>) : <Button className={styles.ok} onClick={closeModal} name="OK" />}
                </div>
            </div>
            </div>, portalRef.current
        )
    )
})

export default Modal;