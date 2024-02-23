import React from "react";

export default function ReviewSetting(props: any) {
  return (
    <div className="flex flex-col border-1 rounded-md shadow-xl custom-height-325 custom-width-325 py-12 px-3 mb-3">
      <h2 className="text-center text-3xl text-[#2298dc] mb-7">
        {props.title}
      </h2>
    </div>
  );
}
