import { FETCH } from "./api-server";

export const loginService = {
    login: async (username, password) => {
        const data = await FETCH.post('public', 'login', { username: username, password: password })
        return data;
    },
    getEvaluatonID: async (session) => {
        const data = await FETCH.get('public', 'client/evaluation/list', { params: { session } });
        return data;
    }
}
