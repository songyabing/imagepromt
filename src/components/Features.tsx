import { BeakerIcon, CursorArrowRaysIcon, LanguageIcon, SparklesIcon } from '@heroicons/react/24/outline';

const features = [
  {
    name: 'Precise Prompt Generation',
    description: 'Our advanced AI algorithms analyze every detail of your image to generate highly accurate and detailed prompts.',
    icon: SparklesIcon,
  },
  {
    name: 'Multi-language Support',
    description: 'Generate prompts in multiple languages to reach a global audience and expand your creative possibilities.',
    icon: LanguageIcon,
  },
  {
    name: 'Easy to Use',
    description: 'Simple drag-and-drop interface or URL input makes it effortless to get started with prompt generation.',
    icon: CursorArrowRaysIcon,
  },
];

export default function Features() {
  return (
    <section id="features" className="py-24 bg-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Powerful Features for Perfect Prompts
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our cutting-edge technology ensures you get the most accurate and detailed prompts for your images.
          </p>
        </div>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-12 max-w-4xl mx-auto">
          {features.map((feature) => (
            <div key={feature.name} className="text-center">
              <div className="inline-flex h-14 w-14 rounded-xl bg-[#3566E3] items-center justify-center mb-4">
                <feature.icon className="h-7 w-7 text-white" aria-hidden="true" />
              </div>
              <div>
                <h3 className="text-xl font-medium text-gray-900 mb-3">{feature.name}</h3>
                <p className="text-base text-gray-500 max-w-sm mx-auto">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
