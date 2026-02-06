import { useState } from "react";
import { motion } from "framer-motion";
import { Input } from "../UI/Input";
import { Button } from "../UI/Button";
import { Card } from "../UI/Card";
import { Checkbox } from "../UI/Checkbox";
import { LoadingOverlay } from "../UI/LoadingOverlay";
import { TermsModal } from "./TermsModal";
import { signUpSchema, type SignUpInput } from "../../lib/schemas/authSchemas";
import { authController } from "../../controllers/authController";

export const SignUpForm = () => {
  const [formData, setFormData] = useState<SignUpInput>({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string>("");
  const [loadingStatus, setLoadingStatus] = useState<"loading" | "success" | "error">("loading");
  const [loadingMessage, setLoadingMessage] = useState("");
  const [termsModal, setTermsModal] = useState<"terms" | "privacy" | null>(null);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    setApiError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setApiError("");

    if (!agreedToTerms) {
      setApiError("Please agree to the Terms and Privacy Policy");
      return;
    }

    const validation = signUpSchema.safeParse(formData);
    if (!validation.success) {
      const fieldErrors: Record<string, string> = {};
      if (validation.error?.issues) {
        validation.error.issues.forEach((err) => {
          if (err.path[0]) {
            fieldErrors[err.path[0].toString()] = err.message;
          }
        });
      }
      setErrors(fieldErrors);
      return;
    }

    setIsLoading(true);
    setLoadingStatus("loading");
    setLoadingMessage("Creating your account...");

    try {
      const response = await authController.signUp(formData);

      if (response.success && response.data) {
        setLoadingStatus("success");
        setLoadingMessage("Account created successfully!");

        setTimeout(() => {
          window.location.href = `/verify-otp?email=${encodeURIComponent(formData.email)}`;
        }, 1500);
      } else {
        setLoadingStatus("error");
        setLoadingMessage(response.message || "Failed to create account");
        setApiError(response.message || "Failed to sign up. Please try again.");
        if (response.errors) {
          setErrors(response.errors as Record<string, string>);
        }

        setTimeout(() => {
          setIsLoading(false);
        }, 2000);
      }
    } catch (error) {
      setLoadingStatus("error");
      setLoadingMessage("An unexpected error occurred");
      setApiError("An unexpected error occurred. Please try again.");

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

      {termsModal && (
        <TermsModal
          isOpen={true}
          onClose={() => setTermsModal(null)}
          type={termsModal}
        />
      )}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md mx-auto"
      >
        <Card className="p-4 sm:p-6 md:p-8">
        <header className="mb-4 sm:mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-1 sm:mb-2">Create Account</h1>
          <p className="text-sm sm:text-base text-gray-400">Sign up to get started</p>
        </header>

        {apiError && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg"
          >
            <p className="text-red-400 text-sm">{apiError}</p>
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
          <Input
            type="text"
            name="fullName"
            label="Full Name"
            placeholder="John Doe"
            value={formData.fullName}
            onChange={handleChange}
            error={errors.fullName}
            autoComplete="name"
          />

          <Input
            type="email"
            name="email"
            label="Email Address"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
            autoComplete="email"
          />

          <Input
            type="password"
            name="password"
            label="Password"
            placeholder="Strong password"
            value={formData.password}
            onChange={handleChange}
            error={errors.password}
            autoComplete="new-password"
          />

          <Input
            type="password"
            name="confirmPassword"
            label="Confirm Password"
            placeholder="Re-enter your password"
            value={formData.confirmPassword}
            onChange={handleChange}
            error={errors.confirmPassword}
            autoComplete="new-password"
          />

          <div className="flex items-start gap-2">
            <Checkbox
              checked={agreedToTerms}
              onChange={(e) => setAgreedToTerms(e.target.checked)}
              className="mt-0.5"
            />
            <p className="text-xs sm:text-sm text-gray-400">
              I agree to the{" "}
              <button
                type="button"
                onClick={() => setTermsModal("terms")}
                className="text-lime-400 hover:text-lime-300 transition-colors underline"
              >
                Terms of Service
              </button>
              {" "}and{" "}
              <button
                type="button"
                onClick={() => setTermsModal("privacy")}
                className="text-lime-400 hover:text-lime-300 transition-colors underline"
              >
                Privacy Policy
              </button>
            </p>
          </div>

          <Button type="submit" variant="primary" fullWidth isLoading={isLoading}>
            Create Account
          </Button>
        </form>

        <footer className="mt-4 sm:mt-6 text-center">
          <p className="text-gray-400 text-xs sm:text-sm">
            Already have an account?{" "}
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
