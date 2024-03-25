"use client";

import React, { useState } from "react";
import captureSettingsData from "./modules/captureSettingsData"; // Importing captureSettingsData module
import metadataData from "./modules/metadataData"; // Importing metadataData module
import CaptureForm from "./components/CaptureForm";
import Loading from "./components/Loading";

/**
 * Home Component
 *
 * This component represents the home page of the application.
 * It includes a header, two columns (Capture Settings and Metadata),
 * and a button.
 */
export default function Home() {
  const allForms = [...captureSettingsData, ...metadataData];
  const [loading, setLoading] = useState(false);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-[#625F63]">
      {/* Conditional rendering of the Loading component */}
      {loading && <Loading />}

      <div className="flex flex-grow w-1/2">
        {/* Rendering Column component with all forms */}
        <CaptureForm
          title="Capture Settings & Metadata"
          forms={allForms}
          setLoading={setLoading}
        />
      </div>
    </div>
  );
}
