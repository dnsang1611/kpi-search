import React, { useState, useContext, useEffect, createContext } from 'react';
import { BACKEND_URL } from '../../constants/apis';

const SessionContext = createContext();
export const useSessionContext = () => useContext(SessionContext);

const SessionProvider = ({children}) => {
    const [metadata, setMetadata] = useState(null);
    const [video, setVideo] = useState(null);

    useEffect(() => {
        const fetchMetadata = async () => {
            const reponse = await fetch(`${BACKEND_URL}/metadata`);
            if (reponse.ok) {
                const data = await reponse.json();
                setMetadata(data);
            } else {
                console.log("Error");
            }
        }

        fetchMetadata();
    }, [])

    return (
        <SessionContext.Provider value={{metadata, video, setVideo}}>
            {children}
        </SessionContext.Provider>
    )
} 

export default SessionProvider;