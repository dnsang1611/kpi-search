const SESSION_ID = 'SESSION_ID';
const EVALUATION_ID = 'EVALUATION_ID';
const ID = 'ID';

export const sessionIdLocal = {
    set: (id) => {
        let json = JSON.stringify(id);
        localStorage.setItem(SESSION_ID, json);
    },
    get: () => {
        let json = localStorage.getItem(SESSION_ID);
        return json && JSON.parse(json);
    },
    remove: () => {
        localStorage.removeItem(SESSION_ID);
    },
}

export const evaluationIdLocal = {
    set: (id) => {
        let json = JSON.stringify(id);
        localStorage.setItem(EVALUATION_ID, json);
    },
    get: () => {
        let json = localStorage.getItem(EVALUATION_ID);
        return json && JSON.parse(json);
    },
    remove: () => {
        localStorage.removeItem(EVALUATION_ID);
    },
}

export const idLocal = {
    set: (id) => {
        let json = JSON.stringify(id);
        localStorage.setItem(ID, json);
    },
    get: () => {
        let json = localStorage.getItem(ID);
        return json && JSON.parse(json);
    },
    remove: () => {
        localStorage.removeItem(ID);
    },
}
