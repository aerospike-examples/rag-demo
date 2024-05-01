import { useContext } from "react";
import { AuthContext } from "../components/auth";

// useAuth is exported
export const useAuth = () => {
    return useContext(AuthContext);
}