import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Modal = ({ isOpen, onClose, title, children }: ModalProps) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleEscape);
      return () => window.removeEventListener("keydown", handleEscape);
    }
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.article
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="
                w-full max-w-2xl max-h-[80vh]
                bg-white/5 backdrop-blur-xl
                border border-white/10
                rounded-2xl
                shadow-[0_8px_32px_0_rgba(0,0,0,0.37)]
                overflow-hidden
                pointer-events-auto
              "
              onClick={(e) => e.stopPropagation()}
            >
              <header className="flex items-center justify-between p-4 sm:p-6 border-b border-white/10">
                <h2 className="text-xl sm:text-2xl font-bold text-white">{title}</h2>
                <button
                  onClick={onClose}
                  className="
                    w-8 h-8 rounded-lg
                    bg-white/5 hover:bg-white/10
                    border border-white/10
                    text-gray-400 hover:text-white
                    transition-all duration-200
                    flex items-center justify-center
                  "
                  aria-label="Close modal"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </header>

              <div className="p-4 sm:p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
                {children}
              </div>
            </motion.article>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
