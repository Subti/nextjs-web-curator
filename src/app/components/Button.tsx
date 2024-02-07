"use client";

import React from "react";

const Button = () => {
  const onClick = () => {
    alert("Hello World!");
  };
  return (
    <button
      className="text-xl rounded-full px-7 py-3 bg-gradient-to-r from-[#2298dc] to-[#7a64a7]"
      onClick={onClick}
    >
      Submit
    </button>
  );
};

export default Button;
