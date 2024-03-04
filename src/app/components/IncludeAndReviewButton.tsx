// components/SaveAndCaptureButton.tsx
"use client"

import React from 'react';
import { useRouter } from 'next/navigation';

const IncludeAndReviewButton = ({ selectedRows }) => {
  const router = useRouter();

  const handleReview = () => {
    if (selectedRows) {
      localStorage.setItem('selectedForReview', JSON.stringify(selectedRows));
      console.log('Selected Items:', selectedRows);
    // Process the selectedRows as needed (e.g., saving to local storage or a global state)
    
      router.push('/review'); // Redirect to the home page
    };
  };

  return (
    <button
      className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      onClick={handleReview}
    >
      Include Selected and Review
    </button>
  );
};

export default IncludeAndReviewButton;
