"use client";

import React from "react";
import { useState } from "react";

interface FormProps {
  label: string;
  id: string;
  value: string;
}

const Form: React.FC<FormProps> = (props) => {
  // Event handler for input change
  const [value, setValue] = useState(props.value);

  // Event handler for input change
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValue(event.target.value);
  };

  // const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  //   onChange(id, event.target.value);
  // };

  return (
    <>
      {/* Rendering label for the form field */}
      <label className="font-bold text-[18px] mb-2">{props.label}:</label>
      {/* Input field */}
      <input
        className="mb-2 py-2 mb-8 custom-border-input"
        type="text"
        id={props.id}
        name={props.id}
        value={value}
        onChange={handleChange} // Binding handleChange function to onChange event
      />
    </>
  );
};

export default Form; // Exporting Form component
