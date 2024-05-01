import { useEffect, useRef } from "react";

//usePortal is exported
export const usePortal = () => {
    const portalRef = useRef(document.createElement("div"));

    useEffect(() => {
        portalRef.current.classList.add("portal");
        document.body.appendChild(portalRef.current);
        return () => {
            document.body.removeChild(portalRef.current);
        }
    }, [])

    return [ portalRef ];
}