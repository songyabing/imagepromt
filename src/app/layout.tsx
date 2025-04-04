import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Script from 'next/script';

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "ImagePrompt - AI-Powered Visual Prompt Generator",
  description: "Smart image analysis generates professional AI art prompts effortlessly",
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
        <Script
          strategy="afterInteractive"
          src="https://www.googletagmanager.com/gtag/js?id=G-VXLS1WQHV2"
        />
        <Script
          id="google-analytics"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-VXLS1WQHV2');
            `
          }}
        />
      </head>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
