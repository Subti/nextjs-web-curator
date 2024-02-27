"use client";

import React, { useState, useEffect } from "react";

interface FormProps {
  label: string;
  id: string;
  value: string;
  onChange: (value: string) => void; // Add this line
}

const Form: React.FC<FormProps> = ({ label, id, value: initialValue, onChange }) => {
  const [currentValue, setCurrentValue] = useState(initialValue);

  useEffect(() => {
    setCurrentValue(initialValue);
  }, [initialValue]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentValue(event.target.value);
    onChange(event.target.value);
  };

  return (
    <>
      <label className="font-bold text-[18px] mb-2">{label}:</label>
      <input
        className="mb-2 py-2 mb-8 custom-border-input"
        type="text"
        id={id}
        name={id}
        value={currentValue}
        onChange={handleChange}
      />
    </>
  );
};

export default Form;