interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  fullWidth?: boolean;
}

export const Button = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  fullWidth = false,
  className = "",
  disabled,
  ...props
}: ButtonProps) => {
  const baseStyles = "font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden";

  const variants = {
    primary: "bg-gradient-to-r from-lime-400 to-lime-500 text-gray-900 hover:from-lime-500 hover:to-lime-600 focus:ring-lime-400/50 shadow-[0_4px_16px_0_rgba(163,230,53,0.4)] hover:shadow-[0_6px_20px_0_rgba(163,230,53,0.6)] hover:scale-[1.02] active:scale-[0.98]",
    secondary: "bg-white/10 backdrop-blur-md border border-white/20 text-white hover:bg-white/20 focus:ring-white/50 hover:border-white/30",
    outline: "bg-transparent border-2 border-lime-400/50 text-lime-400 hover:bg-lime-400/10 hover:border-lime-400 focus:ring-lime-400/50 backdrop-blur-sm",
    ghost: "bg-transparent text-gray-300 hover:bg-white/5 focus:ring-white/50",
  };

  const sizes = {
    sm: "px-3 py-2 text-xs sm:text-sm",
    md: "px-4 py-2.5 sm:py-3 text-sm sm:text-base",
    lg: "px-6 py-3 sm:py-4 text-base sm:text-lg",
  };

  return (
    <button
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${fullWidth ? "w-full" : ""}
        ${isLoading ? "pointer-events-none" : ""}
        ${className}
      `}
      disabled={disabled || isLoading}
      {...props}
    >
      {variant === "primary" && (
        <span className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300"></span>
      )}

      {isLoading && (
        <span className="absolute inset-0 flex items-center justify-center backdrop-blur-sm">
          <svg
            className="animate-spin h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        </span>
      )}
      <span className={`relative z-10 ${isLoading ? "invisible" : ""}`}>{children}</span>
    </button>
  );
};
