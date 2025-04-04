import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "ImagePrompt - Transform Images to Perfect Prompts",
  description: "Transform your images into perfect prompts with our advanced AI technology",
  keywords: ["image to prompt", "AI", "prompt generation", "image analysis"],
  icons: {
    icon: '/favicon.svg'
  },
  verification: {
    google: 'QHUIuwZ89g_3hJY5x3nZbwqETrgWLrOTLRFhe0bPjSo'
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <meta name="google-site-verification" content="QHUIuwZ89g_3hJY5x3nZbwqETrgWLrOTLRFhe0bPjSo" />
      </head>
      <body className={`${inter.className} antialiased bg-white`}>
        {children}
      </body>
    </html>
  );
}
