'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Something went wrong</h2>
        <button
          onClick={() => reset()}
          className="bg-[#3566E3] text-white px-4 py-2 rounded-md hover:bg-[#2952c8] transition-colors"
        >
          Retry
        </button>
      </div>
    </div>
  );
}
