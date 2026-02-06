import { useState } from "react";
import { motion } from "framer-motion";
import { Input } from "../UI/Input";
import { Button } from "../UI/Button";
import { Card } from "../UI/Card";
import { LoadingOverlay } from "../UI/LoadingOverlay";

export const ForgotPasswordForm = () => {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState<"loading" | "success" | "error">("loading");
  const [loadingMessage, setLoadingMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email) {
      setError("Email is required");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address");
      return;
    }

    setIsLoading(true);
    setLoadingStatus("loading");
    setLoadingMessage("Sending reset link...");

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));

      setLoadingStatus("success");
      setLoadingMessage("Reset link sent to your email!");

      setTimeout(() => {
        window.location.href = "/sign-in";
      }, 2000);
    } catch (error) {
      setLoadingStatus("error");
      setLoadingMessage("Failed to send reset link");
      setError("An unexpected error occurred. Please try again.");

      setTimeout(() => {
        setIsLoading(false);
      }, 2000);
    }
  };

  return (
    <>
      <LoadingOverlay
        isVisible={isLoading}
        status={loadingStatus}
        message={loadingMessage}
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md mx-auto"
      >
        <Card className="p-4 sm:p-6 md:p-8">
          <header className="mb-4 sm:mb-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-lime-400/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-lime-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white mb-1 sm:mb-2">Forgot Password?</h1>
            <p className="text-sm sm:text-base text-gray-400">
              Enter your email and we'll send you a reset link
            </p>
          </header>

          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg"
            >
              <p className="text-red-400 text-sm flex items-center gap-2">
                <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {error}
              </p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
            <Input
              type="email"
              name="email"
              label="Email Address"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />

            <Button type="submit" variant="primary" fullWidth isLoading={isLoading}>
              Send Reset Link
            </Button>
          </form>

          <footer className="mt-6 text-center">
            <p className="text-gray-400 text-xs sm:text-sm">
              Remember your password?{" "}
              <a href="/sign-in" className="text-lime-400 hover:text-lime-300 font-medium transition-colors underline">
                Sign in
              </a>
            </p>
          </footer>
        </Card>
      </motion.div>
    </>
  );
};
