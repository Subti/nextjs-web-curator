import React from "react";

/**
 * Select Signal Header Component
 *
 * Represents the select signal header section of the application.
 * Displays a title centered within a colored background.
 */
const SelectSignalHeader = () => {
  return (
    <div className="text-4xl text-white flex relative w-4/5 h-32 bg-[#2298dc] justify-center items-center mb-4">
      Select Signals to Include in Training Dataset:
    </div>
  );
};

export default SelectSignalHeader; // Exporting Header component
