'use client';

import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-white shadow-sm fixed w-full z-50">
      <nav className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Link href="/" className="flex items-center space-x-2">
            <svg className="w-8 h-8 text-[#3566E3]" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-2xl font-bold text-gray-900">ImagePrompt</span>
          </Link>
        </div>
        <div className="hidden md:flex items-center space-x-8">
          <Link href="#features" className="text-gray-600 hover:text-gray-900">Features</Link>
          <Link href="#how-it-works" className="text-gray-600 hover:text-gray-900">How It Works</Link>
          <Link href="#pricing" className="text-gray-600 hover:text-gray-900">Pricing</Link>
          <Link href="#faq" className="text-gray-600 hover:text-gray-900">FAQ</Link>
          <a 
            href="https://t.me/+p-3TKOapvzFjZjM1" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="bg-[#3566E3] text-white px-4 py-2 rounded-md hover:bg-[#2952c8] transition-colors"
          >
            Contact Us
          </a>
        </div>
      </nav>
    </header>
  );
}
