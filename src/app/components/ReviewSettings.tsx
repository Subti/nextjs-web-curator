"use client";

import React, { useEffect, useState } from "react";

interface ReviewSettingProps {
  title: string;
  formData: Record<string, any> | null;
}

// Function component for displaying review settings
export default function ReviewSetting({ title, formData }: ReviewSettingProps) {
  // State hook for storing transformed data
  const [data, setData] = useState({});

  // Function to transform keys of an object to capitalize each word
  function transformKeys(obj: { [key: string]: any }): { [key: string]: any } {
    const transformedObj: { [key: string]: any } = {};
    for (let key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        // Capitalize each word in the key
        const newKey = key
          .split("_")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" ");
        transformedObj[newKey] = obj[key];
      }
    }
    return transformedObj;
  }

  // Effect hook to update data when formData changes
  useEffect(() => {
    if (formData) {
      // Set a timeout to update data after a delay
      const timeout = setTimeout(() => {
        // Transform keys of formData and update data
        setData(transformKeys(formData));
        console.log("Setting Displayed");
      }, 100);

      // Clear the timeout on component unmount or when formData changes
      return () => clearTimeout(timeout);
    }
  }, [formData]);

  // Return JSX for the component
  return (
    <div className="flex flex-col bg-qoherentgray rounded-lg h-[400px] w-[400px] py-8 px-3 mb-3 mt-5">
      <div className="border-t-[1px] border-b-[1px] border-t-qoherentlightgray border-b-qoherentlightgray mb-7 py-4">
        <h2 className="text-center text-3xl text-white transition-all duration-500 hover:text-[#2298dc] hover:scale-105 hover:cursor-pointer">
          {title}
        </h2>
      </div>
      {formData && (
        <div>
          {Object.entries(data).map(([key, value]) => (
            <div key={key}>
              <span className="font-bold text-white">{key}:</span>{" "}
              <span className="text-white">{value as any}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
