import React from "react";

/**
 * Header Component
 *
 * Represents the header section of the application.
 * Displays a title centered within a colored background.
 */
export default function Header(props: any) {
  return (
    <div className="text-4xl text-white flex relative w-4/5 h-32 bg-[#2298dc] justify-center items-center mb-4">
      {props.title}
    </div>
  );
}
