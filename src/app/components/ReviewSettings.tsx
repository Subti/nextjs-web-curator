import React, { useState } from "react";
import Button from "./Button";

interface FormDataItem {
  id: any;
  name: any;
  label: any;
  value: any;
}

interface ReviewSettingProps {
  title: string;
  renderFormAndButton: boolean;
  formData: FormDataItem[] | null;
}

export default function ReviewSetting({
  title,
  renderFormAndButton,
  formData
}: ReviewSettingProps) {
  const [value, setValue] = useState("");

  // Event handler for input change
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValue(event.target.value);
  };

  return (
    <div className="flex flex-col border-1 rounded-md shadow-xl custom-height-400 custom-width-400 py-8 px-3 mb-3">
      <h2 className="text-center text-3xl text-[#2298dc] mb-7">{title}</h2>
      {formData && (
        <div>
          {formData.map((item) => (
            <div key={item.id}>
              <span className="font-bold">{item.label}:</span> {item.value}
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
