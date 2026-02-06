interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: "none" | "sm" | "md" | "lg";
}

export const Card = ({
  children,
  className = "",
  padding = "md",
}: CardProps) => {
  const paddingStyles = {
    none: "",
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  return (
    <article
      className={`
        relative overflow-hidden
        bg-white/[0.03] backdrop-blur-2xl backdrop-saturate-150
        border border-white/[0.08]
        rounded-2xl
        shadow-[0_8px_32px_0_rgba(0,0,0,0.4)]
        before:absolute before:inset-0
        before:bg-gradient-to-br before:from-white/[0.08] before:via-white/[0.02] before:to-transparent
        before:pointer-events-none before:opacity-100
        after:absolute after:inset-0
        after:bg-gradient-to-t after:from-black/20 after:to-transparent
        after:pointer-events-none after:opacity-50
        transition-all duration-300
        hover:border-white/[0.15] hover:shadow-[0_8px_40px_0_rgba(163,230,53,0.12)]
        hover:bg-white/[0.05]
        ${paddingStyles[padding]}
        ${className}
      `}
      style={{
        backdropFilter: 'blur(24px) saturate(150%)',
        WebkitBackdropFilter: 'blur(24px) saturate(150%)',
      }}
    >
      <div className="relative z-10">
        {children}
      </div>
    </article>
  );
};
