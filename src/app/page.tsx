"use client";

import React, { useState } from "react";
import captureSettingsData from "./modules/captureSettingsData";
import metadataData from "./modules/metadataData";
import CaptureForm from "./components/CaptureForm";
import Loading from "./components/Loading";
import Inspect from "@/pages/inspect";

/**
 * Home Component
 *
 * This component represents the home page of the application.
 */
export default function Home() {
  const allForms = [...captureSettingsData, ...metadataData];
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");
  const [inspect, setInspect] = useState(false);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-qoherentlightgray">
      {/* Conditional rendering of the Loading component */}
      {loading && <Loading text={loadingText} />}
      {inspect ? (
        <Inspect
          setInspect={setInspect}
          setLoadingText={setLoadingText}
          setLoading={setLoading}
        />
      ) : (
        <div className="flex flex-grow w-1/2">
          {/* Rendering Column component with all forms */}
          <CaptureForm
            title="Capture Settings & Metadata"
            forms={allForms}
            setLoading={setLoading}
            setLoadingText={setLoadingText}
            setInspect={setInspect}
          />
        </div>
      )}
    </div>
  );
}
