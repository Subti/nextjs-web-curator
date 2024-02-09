import React from "react";
import Column from "./Column";
import Form from "./Form";

const Row = () => {
  return (
    <div className="flex bg-white w-1/2 h-28">
      <Column title="Capture Settings">
        <Form
          label="IP Address"
          id="ip_address"
          name="ip_address"
          value="192.168.40.2"
        />
      </Column>
      <Column title="Metadata" />
    </div>
  );
};

export default Row;
