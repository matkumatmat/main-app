import { forwardRef } from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = "", ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-xs sm:text-sm font-medium text-gray-200 mb-1.5">
            {label}
          </label>
        )}
        <input
          ref={ref}
          autoComplete="off"
          data-form-type="other"
          className={`
            w-full px-3 py-2 sm:px-4 sm:py-3 rounded-lg text-sm sm:text-base
            bg-white/5 backdrop-blur-md
            border border-white/10
            text-white placeholder-gray-400
            shadow-[inset_0_2px_4px_0_rgba(0,0,0,0.2)]
            focus:outline-none focus:ring-2 focus:ring-lime-400/50 focus:border-lime-400/50
            focus:bg-white/10
            transition-all duration-300
            hover:border-white/20
            ${error ? "border-red-500/50 focus:ring-red-500/50 focus:border-red-500/50" : ""}
            ${className}
          `}
          {...props}
        />
        {error && (
          <p className="mt-1.5 text-sm text-red-400 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
