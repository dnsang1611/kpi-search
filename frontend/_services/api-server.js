import { HOST_URL, PUBLIC_API_URL } from "@/app/_constants/api";

const _FETCH = async (type, url, options = {}) => {
    const isFormData = options?.body instanceof FormData;
    const opts = {
        method: options?.method || 'GET',
        ...options,
        body: isFormData ? options?.body : JSON.stringify(options?.body),
        headers: {
            ...options?.headers,
            'Content-Type': isFormData ? undefined : 'application/json',
            Accept: 'application/json',
        },
    };

    if (isFormData && opts.headers) delete opts.headers['Content-Type'];

    try {
        const apiUrl = type === 'public' ? PUBLIC_API_URL : HOST_URL;

        const queries = options.params
            ? `?${new URLSearchParams(options.params).toString()}`
            : '';

        const res = await fetch(`${apiUrl}${url}${queries}`, opts);

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData?.message || 'Request failed');
        }

        const data = await res.json();
        return {
            success: true,
            data,
        };
    } catch (err) {
        return {
            success: false,
            message: err.message,
            statusCode: err.statusCode || 500,
        };
    }
};

export const FETCH = {
    get: async (type, url, options) => await _FETCH(type, url, { method: 'GET', ...options }),
    post: async (type, url, data, options) => await _FETCH(type, url, { method: 'POST', body: data, ...options }),
    put: async (type, url, data, options) => await _FETCH(type, url, { method: 'PUT', body: data, ...options }),
    delete: async (type, url, data, options) => await _FETCH(type, url, { method: 'DELETE', body: data, ...options }),
};
