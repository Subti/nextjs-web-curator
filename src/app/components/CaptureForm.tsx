"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import CaptureInput from "./CaptureInput";
import Button from "./Button";

interface FormData {
  label: string;
  id: string;
  name: string;
  value: string;
}

interface CaptureFormProps {
  title: string;
  forms: FormData[];
}

const CaptureForm: React.FC<CaptureFormProps> = ({ title, forms }) => {
  const router = useRouter();
  const [imageUrl, setImageUrl] = useState(null);
  const [captureSettings, setCaptureSettings] = useState({});
  const [recordingSummary, setRecordingSummary] = useState({});
  const [metadata, setMetadata] = useState({});
  const [formValues, setFormValues] = useState<Record<string, string>>(
    forms.reduce((values, form) => ({ ...values, [form.id]: form.value }), {})
  );

  const handleFormChange = (id: string, value: string) => {
    setFormValues((values) => ({ ...values, [id]: value }));
  };

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

    for (let pair of formData.entries()) {
      console.log(pair[0] + ", " + pair[1]);
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
        if (data) {
          router.push("/inspect");
        }
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col flex-grow w-1/2 py-8 px-3 mb-3"
    >
      <div className="py-5 mb-7 border-b-[1px] border-t-[1px]">
        <h2 className="text-center text-3xl text-white tranform-all hover:scale-105 duration-500 hover:text-[#2298dc] hover:cursor-pointer">
          {title}
        </h2>
      </div>
      {forms.map((formData, index) => (
        <CaptureInput
          key={index}
          {...formData}
          onChange={(value: string) => handleFormChange(formData.id, value)}
        />
      ))}
      <Button text="Submit" type="submit" textSize="xl" />
    </form>
  );
};

export default CaptureForm;
