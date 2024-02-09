import React from "react";
import Form from "./Form"; // Importing Form component

// Interface for the shape of form data
interface FormData {
  label: string;
  id: string;
  name: string;
  value: string;
}

// Interface defining the props for the Column component
interface ColumnProps {
  title: string; // Title of the column
  forms: FormData[]; // Array of form data
}

/**
 * Column Component
 *
 * Represents a column in the layout containing forms.
 * Receives props including a title and an array of form data.
 */
const Column: React.FC<ColumnProps> = ({ title, forms }) => {
  return (
    <div className="flex flex-col flex-grow border-1 rounded-md shadow-xl w-1/2 py-8 px-3 mb-3">
      {/* Rendering the column title */}
      <h2 className="text-center text-3xl text-[#2298dc] mb-7">{title}</h2>
      {/* Iterating over form data and rendering Form component for each */}
      {forms.map((formData, index) => (
        <Form key={index} {...formData} /> // Passing each form data as props to Form component
      ))}
    </div>
  );
};

export default Column; // Exporting Column component
