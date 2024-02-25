import React from "react";
import Column from "./components/Column"; // Importing Column component
import Header from "./components/Header"; // Importing Header component
import captureSettingsForms from "./modules/captureSettingsData"; // Importing captureSettingsForms module
import metadataForms from "./modules/metadataData"; // Importing metadataForms module

/**
 * Home Component
 *
 * This component represents the home page of the application.
 * It includes a header, two columns (Capture Settings and Metadata),
 * and a button.
 */
export default function Home() {
  const allForms = [...captureSettingsForms, ...metadataForms];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      {/* Rendering Header component */}
      <Header title="Capture recording from software defined radio" />
      <div className="flex flex-grow bg-white w-1/2">
        {/* Rendering Column component with all forms */}
        <Column title="Capture Settings & Metadata" forms={allForms} />
      </div>
    </div>
  );
}
