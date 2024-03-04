import React from "react";

/**
 * Header Component
 *
 * Represents the header section of the application.
 * Displays a title centered within a colored background.
 */

interface HeaderProps {
  title: string;
}

export default function Header({ title }: HeaderProps) {
  return (
    <div className="text-4xl text-white flex relative w-full h-32 bg-[#2298dc] justify-center items-center mb-4">
      {title}
    </div>
  );
}
