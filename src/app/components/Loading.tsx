import React from "react";

const Loading = () => {
  return (
    <div className="fixed top-0 left-0 w-screen h-screen z-50 flex justify-center items-center bg-gray-900 bg-opacity-50">
      <div className="flex flex-col gap-5 items-center">
        <h1 className="text-white text-[2rem]">Generating Signal</h1>
        <div className="loader ease-linear rounded-full border-8 border-t-8 border-gray-200 h-24 w-24"></div>
      </div>
    </div>
  );
};

export default Loading;
