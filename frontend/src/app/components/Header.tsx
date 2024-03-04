import React from "react";

/**
 * Header Component
 *
 * Represents the header section of the application.
 * Displays a title centered within a colored background.
 */
const Header = () => {
  return (
    <div className="text-4xl text-white flex relative w-4/5 h-32 bg-[#2298dc] justify-center items-center mb-4">
      Capture recording from software defined radio
    </div>
  );
};

export default Header; // Exporting Header component
