// components/SaveAndCaptureButton.tsx
"use client"

import React from 'react';
import { useRouter } from 'next/navigation';

const IncludeAndCurateButton = ({ selectedRows }) => {
  const router = useRouter();

  const handleSaveAndCapture = () => {
    if (selectedRows) {
      
    // Process the selectedRows as needed (e.g., saving to local storage or a global state)
      localStorage.setItem('selectedForCurate', JSON.stringify(selectedRows));
    router.push('/final'); // Redirect to the home page
    console.log('Selected Items:', selectedRows);
    };
  };

  return (
    <button
      className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      onClick={handleSaveAndCapture}
    >
      Include and Curate
    </button>
  );
};

export default IncludeAndCurateButton;
