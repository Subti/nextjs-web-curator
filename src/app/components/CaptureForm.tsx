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
  setCapture: React.Dispatch<React.SetStateAction<boolean>>;
  setInspect: React.Dispatch<React.SetStateAction<boolean>>;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setLoadingText: React.Dispatch<React.SetStateAction<string>>;
}

const CaptureForm: React.FC<CaptureFormProps> = ({
  title,
  forms,
  setLoading,
  setLoadingText,
  setCapture,
  setInspect
}) => {
  const router = useRouter();

  // State to hold form values
  const [formValues, setFormValues] = useState<Record<string, string>>(
    forms.reduce((values, form) => ({ ...values, [form.id]: form.value }), {})
  );

  // Function to toggle window scrolling to top
  const toggleWindow = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Function to handle form input change
  const handleFormChange = (id: string, value: string) => {
    setFormValues((values) => ({ ...values, [id]: value }));
  };

  // Function to handle form submission
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Process form values
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

    // Create FormData object
    const formData = new FormData();

    // Append form data to FormData object
    for (const key in processedFormValues) {
      formData.append(key, processedFormValues[key].toString());
    }

    // Log FormData entries
    for (let pair of formData.entries()) {
      console.log(pair[0] + ", " + pair[1]);
    }

    try {
      // Set loading state and toggle window scroll
      setLoadingText("Capturing Signal");
      setLoading(true);
      toggleWindow();

      // Send POST request to server
      const response = await fetch("http://localhost:8000/", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        console.error("HTTP error", response.status);
      } else {
        const data = await response.json();
        if (data) {
          // router.push("/inspect");
          setLoading(false);
          setCapture(false);
          setInspect(true);
        }
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  // JSX for the component
  return (
    <div className="flex flex-grow w-1/2">
      <form
        onSubmit={handleSubmit}
        className="flex flex-col flex-grow w-1/2 py-8 px-3 mb-3"
      >
        <div className="py-5 mb-7 border-b-[1px] border-t-[1px] border-qoherentlightgray">
          <h2 className="text-center text-3xl text-white tranform-all hover:scale-105 duration-500 hover:text-qoherentblue hover:cursor-pointer">
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
    </div>
  );
};

export default CaptureForm;
