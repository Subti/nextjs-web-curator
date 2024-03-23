import React from "react";

// Define TextSize interface
interface TextSize {
  sm: string;
  md: string;
  base: string;
  lg: string;
  xl: string;
}

// Define ButtonProps interface
interface ButtonProps {
  textSize: keyof TextSize;
  type: "submit" | "reset" | "button" | undefined;
  text: string;
}

const Button = (props: ButtonProps) => {
  const textSize: TextSize = {
    sm: "text-sm",
    md: "text-md",
    base: "text-base",
    lg: "text-lg",
    xl: "text-xl"
  };

  return (
    <button
      className={`${
        textSize[props.textSize]
      } text-white rounded-lg px-7 py-3 bg-transparent border-[1px] border-white transition-colors duration-500 hover:bg-[#03A9F4] self-center`}
      type={props.type}
    >
      {props.text}
    </button>
  );
};

export default Button;
