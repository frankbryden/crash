import jwt_decode from "jwt-decode";

export default function useTokenDecoded(token) {
    if (token === undefined || token === null) {
        return {};
    }

    const decoded = jwt_decode(token);

    return decoded;
}