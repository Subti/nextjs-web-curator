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
        setRecordingSummary(data.rec_args);
        setCaptureSettings(data.capture_args);
        setMetadata(data.metadata.metadata);
        setImageUrl(data.image_url._url);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  useEffect(() => {
    if (imageUrl && recordingSummary && captureSettings && metadata) {
      router.push(
        `/inspect?image_url=${encodeURIComponent(
          imageUrl
        )}&rec_summary=${encodeURIComponent(
          JSON.stringify(recordingSummary)
        )}&capture_settings=${encodeURIComponent(
          JSON.stringify(captureSettings)
        )}&metadata=${encodeURIComponent(JSON.stringify(metadata))}`
      );
    }
  }, [imageUrl, recordingSummary, captureSettings, metadata, router]);

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col flex-grow border-1 rounded-md shadow-xl w-1/2 py-8 px-3 mb-3"
    >
      <h2 className="text-center text-3xl text-[#2298dc] mb-7">{title}</h2>
      {forms.map((formData, index) => (
        <CaptureInput
          key={index}
          {...formData}
          onChange={(value: string) => handleFormChange(formData.id, value)}
        />
      ))}
      <Button text="Submit" type="submit" />
    </form>
  );
};

export default CaptureForm;
