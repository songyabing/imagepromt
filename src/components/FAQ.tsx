'use client';

import { Disclosure } from '@headlessui/react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

const faqs = [
  {
    question: 'What types of images can I use?',
    answer: 'Our system supports all major image formats including JPG, PNG, WebP, and GIF. You can either upload images directly or provide image URLs.',
  },
  {
    question: 'How accurate are the generated prompts?',
    answer: 'Our AI technology provides highly accurate prompts by analyzing multiple aspects of your images including composition, subjects, lighting, style, and mood. We continuously improve our algorithms to ensure the highest quality results.',
  },
  {
    question: 'Which languages are supported?',
    answer: 'We currently support prompt generation in English and Chinese, with more languages coming soon. Our multi-language support ensures accurate translations while maintaining the technical accuracy of the prompts.',
  },
  {
    question: 'Can I use the generated prompts commercially?',
    answer: 'Yes, all prompts generated through our service can be used for both personal and commercial purposes. There are no restrictions on how you use the output.',
  },
  {
    question: 'Is there an API available?',
    answer: 'Yes, we offer API access with our Pro and Enterprise plans. This allows you to integrate our prompt generation capability directly into your applications and workflows.',
  },
];

export default function FAQ() {
  return (
    <section id="faq" className="py-24 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Everything you need to know about our image prompt generation service
          </p>
        </div>

        <div className="mt-20 max-w-3xl mx-auto">
          <dl className="space-y-6">
            {faqs.map((faq) => (
              <Disclosure
                as="div"
                key={faq.question}
                className="bg-white rounded-lg shadow-sm"
              >
                {({ open }) => (
                  <>
                    <Disclosure.Button className="flex w-full items-center justify-between px-6 py-4">
                      <span className="text-lg font-medium text-gray-900">
                        {faq.question}
                      </span>
                      <ChevronDownIcon
                        className={`${
                          open ? 'rotate-180 transform' : ''
                        } h-5 w-5 text-gray-500`}
                      />
                    </Disclosure.Button>
                    <Disclosure.Panel className="px-6 pb-4">
                      <p className="text-gray-600">{faq.answer}</p>
                    </Disclosure.Panel>
                  </>
                )}
              </Disclosure>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}
