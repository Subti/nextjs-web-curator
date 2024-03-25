import React from "react";

const Loading = () => {
  return (
    <div className="fixed top-0 left-0 w-screen h-screen z-50 flex justify-center items-center bg-gray-900 bg-opacity-50">
      <div className="text-white">Generating Signal...</div>
    </div>
  );
};

export default Loading;
