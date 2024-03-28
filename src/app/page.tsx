"use client";

import React, { useState } from "react";
import captureSettingsData from "./modules/captureSettingsData";
import metadataData from "./modules/metadataData";
import CaptureForm from "./components/CaptureForm";
import Loading from "./components/Loading";
import Inspect from "@/pages/inspect";
import SlicedImages from "@/pages/sliced-images";

/**
 * Home Component
 *
 * This component represents the home page of the application.
 */
export default function Home() {
  const allForms = [...captureSettingsData, ...metadataData];
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");
  const [capture, setCapture] = useState(true);
  const [inspect, setInspect] = useState(false);
  const [sliced, setSliced] = useState(false);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-qoherentlightgray">
      {loading && <Loading text={loadingText} />}
      {capture && (
        <CaptureForm
          title="Capture Settings & Metadata"
          forms={allForms}
          setCapture={setCapture}
          setInspect={setInspect}
          setLoading={setLoading}
          setLoadingText={setLoadingText}
        />
      )}
      {inspect && (
        <Inspect
          setLoadingText={setLoadingText}
          setLoading={setLoading}
          setCapture={setCapture}
          setInspect={setInspect}
          setSliced={setSliced}
        />
      )}
      {sliced && <SlicedImages />}
    </div>
  );
}
