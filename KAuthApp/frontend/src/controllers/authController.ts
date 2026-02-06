import { makeRequest, type ApiResponse } from "../lib/api/apiClient";
import type { SignInInput, SignUpInput, OtpInput, ResendOtpInput } from "../lib/schemas/authSchemas";

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface User {
  id: string;
  email: string;
  fullName: string;
  isVerified: boolean;
  createdAt: string;
}

export interface SignInResponse {
  user: User;
  tokens: AuthTokens;
}

export interface SignUpResponse {
  user: User;
  message: string;
}

export interface OtpVerificationResponse {
  user: User;
  tokens: AuthTokens;
  message: string;
}

class AuthController {
  async signIn(data: SignInInput): Promise<ApiResponse<SignInResponse>> {
    return makeRequest<SignInResponse>({
      method: "POST",
      url: "/signin",
      data,
    });
  }

  async signUp(data: SignUpInput): Promise<ApiResponse<SignUpResponse>> {
    return makeRequest<SignUpResponse>({
      method: "POST",
      url: "/signup",
      data: {
        email: data.email,
        password: data.password,
        fullName: data.fullName,
      },
    });
  }

  async verifyOtp(data: OtpInput & { email: string }): Promise<ApiResponse<OtpVerificationResponse>> {
    return makeRequest<OtpVerificationResponse>({
      method: "POST",
      url: "/verify-otp",
      data,
    });
  }

  async resendOtp(data: ResendOtpInput): Promise<ApiResponse<{ message: string }>> {
    return makeRequest<{ message: string }>({
      method: "POST",
      url: "/resend-otp",
      data,
    });
  }

  async signOut(): Promise<ApiResponse<{ message: string }>> {
    return makeRequest<{ message: string }>({
      method: "POST",
      url: "/signout",
    });
  }

  storeTokens(tokens: AuthTokens): void {
    localStorage.setItem("accessToken", tokens.accessToken);
    localStorage.setItem("refreshToken", tokens.refreshToken);
  }

  clearTokens(): void {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  }

  getAccessToken(): string | null {
    return localStorage.getItem("accessToken");
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}

export const authController = new AuthController();
