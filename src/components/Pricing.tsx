'use client';

const tiers = [
  {
    name: 'Free',
    price: '0',
    features: [
      '10 prompts per month',
      'Basic image analysis',
      'English language support',
      'Standard response time',
    ],
    cta: 'Get Started',
    mostPopular: false,
  },
  {
    name: 'Pro',
    price: '9.99',
    features: [
      'Unlimited prompts',
      'Advanced image analysis',
      'Multi-language support',
      'Priority response time',
      'API access',
      'Email support',
    ],
    cta: 'Start Free Trial',
    mostPopular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    features: [
      'Custom prompt generation',
      'Dedicated account manager',
      'Custom API integration',
      '24/7 phone support',
      'SLA guarantees',
      'Custom features',
    ],
    cta: 'Contact Sales',
    mostPopular: false,
  },
];

export default function Pricing() {
  return (
    <section id="pricing" className="py-24 bg-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Choose the perfect plan for your needs
          </p>
        </div>

        <div className="mt-20 grid grid-cols-1 gap-8 lg:grid-cols-3">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={`relative rounded-2xl ${
                tier.mostPopular
                  ? 'bg-[#3566E3] text-white shadow-xl scale-105'
                  : 'bg-gray-50 text-gray-900'
              } p-8`}
            >
              {tier.mostPopular && (
                <div className="absolute top-0 -translate-y-1/2 left-1/2 -translate-x-1/2">
                  <span className="inline-flex rounded-full bg-green-500 px-4 py-1 text-sm font-semibold text-white">
                    Most Popular
                  </span>
                </div>
              )}
              <div className="mb-8">
                <h3 className="text-2xl font-bold mb-4">{tier.name}</h3>
                <div className="flex items-baseline gap-x-2">
                  <span className="text-4xl font-bold">${tier.price}</span>
                  {tier.price !== 'Custom' && (
                    <span className={tier.mostPopular ? 'text-gray-300' : 'text-gray-600'}>
                      /month
                    </span>
                  )}
                </div>
              </div>
              <ul className="space-y-4 mb-8">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-x-2">
                    <svg
                      className={`h-5 w-5 ${
                        tier.mostPopular ? 'text-green-400' : 'text-green-500'
                      }`}
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <button
                className={`w-full py-3 px-6 rounded-lg font-medium ${
                  tier.mostPopular
                    ? 'bg-white text-[#3566E3] hover:bg-gray-100'
                    : 'bg-[#3566E3] text-white hover:bg-[#2952c8]'
                } transition-colors`}
              >
                {tier.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
