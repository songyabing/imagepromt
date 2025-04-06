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
  description: "Transform any image into perfect AI prompts. Our advanced AI technology helps you describe images and generate accurate prompts for Midjourney, Stable Diffusion, and other AI art models.",
  keywords: [
    // 单个关键词
    "image", "prompt", "ai", "generator", "images", "describe", "generate", "generated", "models",
    // 组合关键词
    "image to prompt", "prompt generator", "ai image", "describe image",
    "image prompt generator", "ai prompt generator", "image description tool",
    // 功能相关
    "image analysis", "visual prompt", "ai art prompts", "midjourney prompts",
    "stable diffusion prompts", "dall-e prompts", "ai image generation",
    // 长尾关键词
    "convert image to prompt", "image prompt optimization", "ai art description",
    "professional prompt generator", "accurate image description"
  ],
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
            `,
          }}
        />
      </head>
      <body className={`${inter.className} antialiased bg-white`}>
        {children}
      </body>
    </html>
  );
}
