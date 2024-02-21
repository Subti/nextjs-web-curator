import React from "react";
import Header from "@/app/components/Header"; // Importing Header component
import ReviewSettings from "@/app/components/ReviewSettings";

export default function Inspect(props: any) {
  return (
    <div className="flex flex-col items-center justify-center">
      <Header title="Inspect Recording" />
      <ReviewSettings />
    </div>
  );
}

// min-h-screen
