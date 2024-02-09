import React from "react";
import Button from "./components/Button";
import Column from "./components/Column";
import Header from "./components/Header";
import captureSettingsForms from "./modules/captureSettingsForms";
import metadataForms from "./modules/metadataForms";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <Header />
      <div className="flex flex-grow bg-white w-1/2">
        <Column title="Capture Settings" forms={captureSettingsForms} />
        <Column title="Metadata" forms={metadataForms} />
      </div>
      <Button />
    </div>
  );
}
