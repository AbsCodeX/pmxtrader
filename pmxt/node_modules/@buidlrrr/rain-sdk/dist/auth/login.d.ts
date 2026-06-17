import { LoginParams, LoginResult } from './types.js';
export declare function loginUser(params: LoginParams & {
    apiUrl: string;
}): Promise<LoginResult>;
