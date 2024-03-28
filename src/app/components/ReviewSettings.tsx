"use client";

import React, { useEffect, useState } from "react";

interface ReviewSettingProps {
  title: string;
  formData: Record<string, any> | null;
}

export default function ReviewSetting({ title, formData }: ReviewSettingProps) {
  const [data, setData] = useState({});

  function transformKeys(obj: { [key: string]: any }): { [key: string]: any } {
    const transformedObj: { [key: string]: any } = {};
    for (let key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        const newKey = key
          .split("_")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" ");
        transformedObj[newKey] = obj[key];
      }
    }
    return transformedObj;
  }

  useEffect(() => {
    if (formData) {
      const timeout = setTimeout(() => {
        setData(transformKeys(formData));
        console.log("Setting Displayed");
      }, 100);

      return () => clearTimeout(timeout);
    }
  }, [formData]);

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
