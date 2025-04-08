import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Page not found</h2>
        <Link
          href="/"
          className="bg-[#3566E3] text-white px-4 py-2 rounded-md hover:bg-[#2952c8] transition-colors"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
}
