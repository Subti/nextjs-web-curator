import React from "react";
import Header from "../app/components/Header"; // Importing Header component
import "../app/globals.css"; // Importing global CSS styles

export default function Inspect(props: any) {
  return (
    <div className="flex flex-col items-center justify-center">
      <Header title="Inspect Recording" />
    </div>
  );
}

// min-h-screen
