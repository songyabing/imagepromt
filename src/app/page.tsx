'use client';

import dynamic from 'next/dynamic';

const Hero = dynamic(() => import('@/components/Hero'), { ssr: false });
const Header = dynamic(() => import('@/components/Header'));
const Features = dynamic(() => import('@/components/Features'));
const HowItWorks = dynamic(() => import('@/components/HowItWorks'));
const Pricing = dynamic(() => import('@/components/Pricing'));
const FAQ = dynamic(() => import('@/components/FAQ'));
const Footer = dynamic(() => import('@/components/Footer'));

export default function Home() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Pricing />
        <FAQ />
      </main>
      <Footer />
    </div>
  );
}
