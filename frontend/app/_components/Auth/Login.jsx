import { PASSWORD, USER_NAME } from '@/_constants/account';
import React, { useState } from 'react';
import { loginService } from '@/_services/login';
import { evaluationIdLocal, sessionIdLocal } from '@/_services/localServices';

const Login = () => {
    const [isLogin, setIsLogin] = useState(false)

    const handleLogin = async () => {
        try {
            const loginResponse = await loginService.login(USER_NAME, PASSWORD);

            if (loginResponse.success) {
                const sessionId = loginResponse.data.sessionId;
                sessionIdLocal.set(sessionId);

                const evaluationResponse = await loginService.getEvaluatonID(sessionId);

                if (evaluationResponse.success) {
                    const evalId = evaluationResponse.data?.[0]?.id;
                    evaluationIdLocal.set(evalId);
                    setIsLogin(true);
                    toast.success('Login successfully!')
                } else {
                    console.error('Failed to fetch evaluation ID:', evaluationResponse.message);
                }
            } else {
                console.error('Login failed:', loginResponse.message);
            }
        } catch (error) {
            console.error('Error during login:', error);
        } finally {
            setIsLogin(true);
        }
    };

    return (
        <div>
            {
                isLogin ? (
                    <div>
                        {/* Handle login */}
                    </div>
                ) : (
                    <button
                        className='text-xs font-medium px-2 py-1 bg-blue-600 size-fit text-white hover:bg-blue-700 rounded-full'
                        onClick={handleLogin}
                    >
                        <span>Login</span>
                    </button>)
            }
        </div>
    );
};

export default Login;
