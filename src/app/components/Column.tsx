import React from "react";
import Form from "./Form";

interface FormData {
  label: string;
  id: string;
  name: string;
  value: string;
}

interface ColumnProps {
  title: string;
  forms: FormData[];
}

const Column: React.FC<ColumnProps> = ({ title, forms }) => {
  return (
    <div className="flex flex-col flex-grow border-1 rounded-md shadow-xl w-1/2 py-8 px-3 mb-3">
      <h2 className="text-center text-3xl text-[#2298dc] mb-7">{title}</h2>
      {forms.map((formData, index) => (
        <Form key={index} {...formData} />
      ))}
    </div>
  );
};

export default Column;
