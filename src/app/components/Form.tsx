"use client";

import React from "react";

interface FormProps {
  label: string;
  id: string;
  value: string;
  onChange: (id: string, value: string) => void;
}

const Form: React.FC<FormProps> = ({ label, id, value, onChange }) => {
  // Event handler for input change
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(id, event.target.value);
  };

  return (
    <>
      {/* Rendering label for the form field */}
      <label className="font-bold text-[18px] mb-2">{label}:</label>
      {/* Input field */}
      <input
        className="mb-2 py-2 mb-8 custom-border-input"
        type="text"
        id={id}
        name={id}
        value={value}
        onChange={handleChange} // Binding handleChange function to onChange event
      />
    </>
  );
};

export default Form; // Exporting Form component