"use client";

import React from "react";
import { useState } from "react";

const Form = (props: any) => {
  const [value, setValue] = useState(props.value);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValue(event.target.value);
  };

  return (
    <>
      <label className="font-bold text-[18px] mb-2">{props.label}:</label>
      <input
        className="mb-2 py-2 mb-8 custom-border-input"
        type="text"
        id={props.id}
        name={props.id}
        value={value}
        onChange={handleChange}
      />
    </>
  );
};

export default Form;
