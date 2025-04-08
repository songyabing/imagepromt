'use client';

import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function Terms() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow pt-24 pb-16 px-4">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Terms of Service</h1>
          <div className="prose prose-blue max-w-none">
            <p className="text-sm text-gray-500 mb-8">Last Updated: March 22, 2025</p>
            
            <h2 className="text-xl font-medium mb-4">Language</h2>
            <p className="text-gray-700 mb-6">
              These Terms of Service are written in English. If these terms are translated into any other language, the English version shall prevail in the event of any conflict or discrepancy.
            </p>

            <p className="text-gray-700 mb-8">
              These Terms of Service ("Terms") govern your use of the Image Prompt website at https://imageprompt.vip ("Website") and the services provided by Image Prompt. By using our Website and services, you agree to these Terms.
            </p>

            <h2 className="text-2xl font-semibold mt-8 mb-4">1. Description of Image Prompt</h2>
            <p className="text-gray-700 mb-6">
              Image Prompt is a platform offering tools and services to help users generate high-quality images and image prompts. Our services include image generation and prompt creation tools designed to enhance your creative process.
            </p>

            <h2 className="text-2xl font-semibold mt-8 mb-4">2. Ownership and Usage Rights</h2>
            <div className="text-gray-700 mb-6">
              <p className="mb-4">2.1 All rights to the Website and related services are owned by Image Prompt.</p>
              <p className="mb-4">2.2 When you generate an image or image prompt using Image Prompt, you gain the right to download and use the image or prompt for any lawful purpose. For any images or prompts you upload, you must ensure you have the necessary intellectual property rights or permissions.</p>
              <p>2.3 You may only use our services through the Website interface provided by Image Prompt. Any unauthorized use, including but not limited to scraping, automated access, or direct API calls outside of our publicly documented API, is strictly prohibited.</p>
            </div>

            <h2 className="text-2xl font-semibold mt-8 mb-4">3. User Data and Privacy</h2>
            <div className="text-gray-700 mb-6">
              <p className="mb-4">3.1 We collect and store user data, including name, email, and payment information, as necessary to provide our services.</p>
              <p>3.2 We handle your data in accordance with our Privacy Policy, which can be found at https://imageprompt.vip/privacy-policy.</p>
            </div>

            <h2 className="text-2xl font-semibold mt-8 mb-4">4. Non-Personal Data Collection</h2>
            <p className="text-gray-700 mb-6">
              We use web cookies to collect non-personal data to improve our services and user experience.
            </p>

            <h2 className="text-2xl font-semibold mt-8 mb-4">5. Disclaimer</h2>
            <div className="text-gray-700 mb-6">
              <p className="mb-4">5.1 We strive to ensure the availability and stability of our services but are not liable for any interruptions or failures.</p>
              <p>5.2 We are not responsible for any direct or indirect losses resulting from your use of the Website and services.</p>
            </div>

            <h2 className="text-2xl font-semibold mt-8 mb-4">6. Governing Law and Dispute Resolution</h2>
            <p className="text-gray-700 mb-6">
              These Terms are governed by the laws of Delaware, United States. Any dispute arising from these Terms shall be resolved through binding arbitration in accordance with the American Arbitration Association rules in Delaware, United States.
            </p>

            <h2 className="text-2xl font-semibold mt-8 mb-4">7. Age Restrictions</h2>
            <p className="text-gray-700 mb-6">
              You must be at least 13 years old to use our services. If you are under 18, you must have parental consent to use our services.
            </p>

            <h2 className="text-2xl font-semibold mt-8 mb-4">8. Service Termination</h2>
            <p className="text-gray-700 mb-6">
              We reserve the right to terminate or suspend your access to our services at our sole discretion, without prior notice, for any violation of these Terms or for any other reason.
            </p>

            <h2 className="text-2xl font-semibold mt-8 mb-4">9. Updates to the Terms</h2>
            <p className="text-gray-700 mb-6">
              We may update these Terms from time to time. Users will be notified of any changes via email. Continued use of the Website and services constitutes acceptance of the updated Terms.
            </p>

            <p className="text-gray-700 mb-4">
              For any questions or concerns regarding, please <a href="https://t.me/+p-3TKOapvzFjZjM1" className="text-[#3566E3] hover:text-[#2952c8] transition-colors">contact us</a>.
            </p>

            <p className="text-gray-700 mt-8 font-medium">
              Thank you for using Image Prompt!
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
