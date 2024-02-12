"use client";

import React, { useState } from "react";
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
  // Create a state object to hold the values of all forms in the column
  const [formValues, setFormValues] = useState<Record<string, string>>(
    forms.reduce((values, form) => ({ ...values, [form.id]: form.value }), {})
  );

  // Function to handle form value changes
  const handleFormChange = (id: string, value: string) => {
    setFormValues(values => ({ ...values, [id]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Convert form values to their appropriate types
    const processedFormValues: { [key: string]: string | number } = {
      ...formValues,
    };

    if (formValues.num_samples) {
      processedFormValues.num_samples = parseInt(formValues.num_samples);
    }
    if (formValues.center_frequency) {
      processedFormValues.center_frequency = parseFloat(formValues.center_frequency);
    }
    if (formValues.gain) {
      processedFormValues.gain = parseFloat(formValues.gain);
    }
    if (formValues.channel) {
      processedFormValues.channel = parseInt(formValues.channel);
    }

    // Create a FormData object
    const formData = new FormData();

    // Add processed form values to the FormData object
    for (const key in processedFormValues) {
      formData.append(key, processedFormValues[key].toString());
    }

    // Log the contents of formData
    for (let pair of formData.entries()) {
      console.log(pair[0] + ', ' + pair[1]);
    }

    try {
      const response = await fetch('http://localhost:8000/', {
        method: 'POST',
        body: formData,  // Send the FormData object
      });

      if (!response.ok) {
        console.error('HTTP error', response.status);
      } else {
        // Do something with the response
        const data = await response.json();
        console.log(data);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col flex-grow border-1 rounded-md shadow-xl w-1/2 py-8 px-3 mb-3">
      <h2 className="text-center text-3xl text-[#2298dc] mb-7">{title}</h2>
      {forms.map((formData, index) => (
        <Form
          key={index}
          {...formData}
          value={formValues[formData.id]}
          onChange={(value) => handleFormChange(formData.id, value)}
        />
      ))}
      <button type="submit">Submit</button>
    </form>
  );
};

export default Column;