'use client';

import Image from 'next/image';

const steps = [
  {
    number: '01',
    title: 'Upload Image',
    description: 'Simply drag and drop your image or paste a URL. We support all major image formats.',
  },
  {
    number: '02',
    title: 'Select Language',
    description: 'Choose your preferred language for the generated prompt from our supported options.',
  },
  {
    number: '03',
    title: 'Generate Prompt',
    description: 'Our AI analyzes your image and generates a detailed, accurate prompt in seconds.',
  },
  {
    number: '04',
    title: 'Use Prompt',
    description: 'Copy your generated prompt and use it for your creative projects.',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-16 bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-10 text-center">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
        <p className="text-lg text-gray-600 mb-10">
          Get perfect prompts in four simple steps
        </p>

        <div className="mt-14 grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step) => (
            <div
              key={step.number}
              className="relative bg-white p-6 rounded-2xl shadow-sm hover:shadow-md transition-shadow text-left"
            >
              <div className="text-4xl font-bold text-black/10 absolute top-4 right-4">
                {step.number}
              </div>
              <div className="relative">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {step.title}
                </h3>
                <p className="text-gray-600">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
