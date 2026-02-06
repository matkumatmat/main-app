import { forwardRef, useId } from "react";

interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, className = "", id, ...props }, ref) => {
    const generatedId = useId();
    const checkboxId = id || generatedId;

    return (
      <label htmlFor={checkboxId} className={`flex items-center gap-2 cursor-pointer group ${className}`}>
        <div className="relative">
          <input
            ref={ref}
            type="checkbox"
            id={checkboxId}
            className="peer sr-only"
            {...props}
          />
          <div className="
            w-5 h-5 rounded-md
            bg-white/5 backdrop-blur-md
            border-2 border-white/20
            transition-all duration-300
            peer-checked:bg-gradient-to-br peer-checked:from-lime-400 peer-checked:to-lime-500
            peer-checked:border-lime-400
            peer-focus:ring-2 peer-focus:ring-lime-400/50 peer-focus:ring-offset-2 peer-focus:ring-offset-transparent
            group-hover:border-white/30
            peer-disabled:opacity-50 peer-disabled:cursor-not-allowed
            flex items-center justify-center
          ">
            <svg
              className="w-3 h-3 text-gray-900 opacity-0 peer-checked:opacity-100 transition-opacity duration-200"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth="3"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        {label && (
          <span className="text-xs sm:text-sm text-gray-300 select-none group-hover:text-gray-200 transition-colors">
            {label}
          </span>
        )}
      </label>
    );
  }
);

Checkbox.displayName = "Checkbox";
