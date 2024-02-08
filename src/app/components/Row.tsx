import React from "react";
import Column from "./Column";

const Row = () => {
  return (
    <div className="flex bg-white w-1/2 h-28">
      <Column />
      <Column />
    </div>
  );
};

export default Row;
