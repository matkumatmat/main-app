import { Modal } from "../UI/Modal";

interface TermsModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: "terms" | "privacy";
}

export const TermsModal = ({ isOpen, onClose, type }: TermsModalProps) => {
  const content = {
    terms: {
      title: "Terms of Service",
      sections: [
        {
          heading: "1. Acceptance of Terms",
          content: "By accessing and using KAuth, you accept and agree to be bound by the terms and provision of this agreement."
        },
        {
          heading: "2. Use License",
          content: "Permission is granted to temporarily use KAuth for personal, non-commercial transitory viewing only."
        },
        {
          heading: "3. User Account",
          content: "You are responsible for maintaining the confidentiality of your account and password. You agree to accept responsibility for all activities that occur under your account."
        },
        {
          heading: "4. Privacy",
          content: "Your use of KAuth is also governed by our Privacy Policy. Please review our Privacy Policy, which also governs the site and informs users of our data collection practices."
        },
        {
          heading: "5. Prohibited Uses",
          content: "You may not use KAuth for any illegal or unauthorized purpose. You must not, in the use of the service, violate any laws in your jurisdiction."
        },
        {
          heading: "6. Termination",
          content: "We may terminate or suspend your account and bar access to the service immediately, without prior notice or liability, under our sole discretion, for any reason whatsoever."
        }
      ]
    },
    privacy: {
      title: "Privacy Policy",
      sections: [
        {
          heading: "1. Information We Collect",
          content: "We collect information you provide directly to us, such as when you create an account, including your name, email address, and password."
        },
        {
          heading: "2. How We Use Your Information",
          content: "We use the information we collect to provide, maintain, and improve our services, to communicate with you, and to monitor and analyze trends and usage."
        },
        {
          heading: "3. Information Sharing",
          content: "We do not share your personal information with third parties except as described in this policy or with your consent."
        },
        {
          heading: "4. Data Security",
          content: "We use AES-256-GCM encryption and Argon2id key derivation to protect your data. However, no method of transmission over the Internet is 100% secure."
        },
        {
          heading: "5. Data Retention",
          content: "We retain your information for as long as your account is active or as needed to provide you services."
        },
        {
          heading: "6. Your Rights",
          content: "You have the right to access, update, or delete your personal information at any time through your account settings."
        }
      ]
    }
  };

  const { title, sections } = content[type];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div className="space-y-6 text-gray-300">
        <p className="text-sm text-gray-400">
          Last updated: {new Date().toLocaleDateString()}
        </p>

        {sections.map((section, index) => (
          <section key={index} className="space-y-2">
            <h3 className="text-lg font-semibold text-white">{section.heading}</h3>
            <p className="text-sm leading-relaxed">{section.content}</p>
          </section>
        ))}

        <footer className="pt-4 border-t border-white/10">
          <p className="text-xs text-gray-500">
            For questions about these {type === "terms" ? "terms" : "policies"}, please contact us at support@kauth.com
          </p>
        </footer>
      </div>
    </Modal>
  );
};
