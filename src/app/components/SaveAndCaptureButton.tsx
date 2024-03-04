// components/SaveAndCaptureButton.tsx
"use client"

import React from 'react';
import { useRouter } from 'next/navigation';

const SaveAndCaptureButton = ({ selectedRows }) => {
  const router = useRouter();

  const handleSaveAndCapture = () => {
    if (selectedRows) {
      console.log('Selected Items:', selectedRows);
      localStorage.setItem('selectedForResult', JSON.stringify(selectedRows));
    // Process the selectedRows as needed (e.g., saving to local storage or a global state)
    
    router.push('/'); // Redirect to the home page
    };
  };

  return (
    <button
      className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      onClick={handleSaveAndCapture}
    >
      Save and Capture More
    </button>
  );
};

export default SaveAndCaptureButton;
