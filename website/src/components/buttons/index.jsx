import React from "react";
import styles from './index.module.css';
import clsx from "clsx";

export const Button = (props) => {
    const { img, className, onClick, name, ...rest } = props;
    return (
        <button 
            className={clsx(styles.btn, className)} 
            onClick={onClick} 
            {...rest}
        >
            {img && img}{name && <span>{name}</span>}
        </button>
    )
}