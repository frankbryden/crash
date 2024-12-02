import { useRouteError } from "react-router-dom";
import Login from "./auth/Login";
import useToken from "./auth/useToken";

function ErrorBoundary() {
    const error = useRouteError();
    const { token, setToken } = useToken();

    if (error?.status === 401) {
        if (token) {
            setToken(null);
        }
        return <Login />;
    }

    // Handle other types of errors or provide a generic fallback
    return <p>Something went wrong. Please try again later.</p>;
}

export default ErrorBoundary;
