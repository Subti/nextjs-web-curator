import React from "react";
import Header from "@/app/components/Header"; // Importing Header component
import ReviewSettings from "@/app/components/ReviewSettings";
import Button from "@/app/components/Button";

export default function Inspect(props: any) {
  return (
    <div className="flex flex-col items-center justify-center">
      <Header title="Inspect Recording" />
      <div className="flex justify-around w-3/4">
        <ReviewSettings />
        <ReviewSettings />
        <ReviewSettings />
      </div>
      <Button text="Discard and Capture New" />
    </div>
  );
}

// min-h-screen
