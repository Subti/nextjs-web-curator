"use client";

import React from "react";
import { useState } from "react";

/**
 * Form Component
 *
 * Represents an input form field with a label.
 * Receives props including label, id, and value.
 * Utilizes React hooks for managing state.
 */
const Form = (props: any) => {
  // State variable to manage the value of the input field
  const [value, setValue] = useState(props.value);

  // Event handler for input change
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValue(event.target.value);
  };

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
