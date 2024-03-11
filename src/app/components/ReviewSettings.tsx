"use client";

import React, { useEffect, useState } from "react";
import Button from "./Button";

interface ReviewSettingProps {
  title: string;
  renderFormAndButton: boolean;
  formData: Record<string, any> | null;
}

export default function ReviewSetting({
  title,
  renderFormAndButton,
  formData
}: ReviewSettingProps) {
  const [value, setValue] = useState("");
  const [data, setData] = useState({});

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValue(event.target.value);
  };

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
    <div className="flex flex-col border-1 rounded-md shadow-xl custom-height-400 custom-width-400 py-8 px-3 mb-3">
      <h2 className="text-center text-3xl text-[#2298dc] mb-7">{title}</h2>
      {formData && (
        <div>
          {Object.entries(data).map(([key, value]) => (
            <div key={key}>
              <span className="font-bold">{key}:</span> {value as any}
            </div>
          ))}
        </div>
      )}
      {renderFormAndButton && (
        <div className="flex flex-col justify-center items-center">
          <p>Enter the cut points as space seperated values</p>
          <br />
          <p>For example: 10 18 25 30...</p>
          <form>
            <input
              className="mb-2 py-2 mb-8 border border-black border-solid rounded-md w-60 mt-5"
              type="text"
              // id={props.id}
              // name={props.id}
              value={value}
              onChange={handleChange} // Binding handleChange function to onChange event
            />
          </form>
          <Button type="submit" text="Save and Prune" />
        </div>
      )}
    </div>
  );
}
