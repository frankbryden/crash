import { useState } from 'react';

export default function useErrorQueue() {
    const [errorQueue, setErrorQueue] = useState([]);

    const addError = (error, timeout = 3) => {
        setTimeout(() => setErrorQueue(eq => [...eq.slice(1)]), timeout * 1000);
        setErrorQueue(eq => [...eq, error]);
    };

    return {
        errorQueue,
        addError
    }
}