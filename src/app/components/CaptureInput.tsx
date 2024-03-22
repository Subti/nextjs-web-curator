"use client";

import React from "react";
import { useState } from "react";

interface CaptureInputProps {
  label: string;
  id: string;
  value: string;
  onChange: (value: string) => void; // Define the onChange prop
}

const CaptureInput: React.FC<CaptureInputProps> = (props) => {
  // Event handler for input change
  const [value, setValue] = useState(props.value);

  // Event handler for input change
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setValue(value); // Update local state
    props.onChange(value); // Forward value to parent component
  };

  return (
    <>
      {/* Rendering label for the CaptureInput field */}
      <label className="font-bold text-[18px] mb-2 text-white">
        {props.label}:
      </label>
      {/* Input field */}
      <input
        className="mb-2 py-2 mb-8 bg-[#222] text-white border-[1px] border-[#625F63] rounded-lg focus:border-[#E63462]"
        type="text"
        id={props.id}
        name={props.id}
        value={value}
        onChange={handleChange} // Binding handleChange function to onChange event
      />
    </>
  );
};

export default CaptureInput; // Exporting CaptureInput component
