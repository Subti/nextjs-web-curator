"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Form from "./Form";
import Button from "./Button";

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
  const router = useRouter();
  const [plotData, setPlotData] = useState(null);
  const [formValues, setFormValues] = useState<Record<string, string>>(
    forms.reduce((values, form) => ({ ...values, [form.id]: form.value }), {})
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const processedFormValues: { [key: string]: string | number } = {
      ...formValues
    };

    if (formValues.num_samples) {
      processedFormValues.num_samples = parseInt(formValues.num_samples);
    }
    if (formValues.center_frequency) {
      processedFormValues.center_frequency = parseFloat(
        formValues.center_frequency
      );
    }
    if (formValues.gain) {
      processedFormValues.gain = parseFloat(formValues.gain);
    }
    if (formValues.channel) {
      processedFormValues.channel = parseInt(formValues.channel);
    }

    const formData = new FormData();

    for (const key in processedFormValues) {
      formData.append(key, processedFormValues[key].toString());
    }

    try {
      const response = await fetch("http://localhost:8000/", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        console.error("HTTP error", response.status);
      } else {
        const data = await response.json();
        console.log(data);
        setPlotData(data.plot_data); // Updated this line
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  useEffect(() => {
    if (plotData) {
      const plotDataParam = encodeURIComponent(JSON.stringify(plotData));
      router.push(`/plotly-test?plotData=${plotDataParam}`);
    }
  }, [plotData, router]);

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col flex-grow border-1 rounded-md shadow-xl w-1/2 py-8 px-3 mb-3"
    >
      <h2 className="text-center text-3xl text-[#2298dc] mb-7">{title}</h2>
      {forms.map((formData, index) => (
        <Form key={index} {...formData} />
      ))}
      <Button />
    </form>
  );
};

export default Column;