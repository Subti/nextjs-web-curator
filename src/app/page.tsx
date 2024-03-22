"use client";

import React from "react";
import Header from "./components/Header"; // Importing Header component
import captureSettingsData from "./modules/captureSettingsData"; // Importing captureSettingsData module
import metadataData from "./modules/metadataData"; // Importing metadataData module
import CaptureForm from "./components/CaptureForm";

/**
 * Home Component
 *
 * This component represents the home page of the application.
 * It includes a header, two columns (Capture Settings and Metadata),
 * and a button.
 */
export default function Home() {
  const allForms = [...captureSettingsData, ...metadataData];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-[#625F63]">
      {/* Rendering Header component */}
      <Header title="Capture recording from software defined radio" />
      <div className="flex flex-grow w-1/2">
        {/* Rendering Column component with all forms */}
        <CaptureForm title="Capture Settings & Metadata" forms={allForms} />
      </div>
    </div>
  );
}
