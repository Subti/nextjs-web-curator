import React from "react";

const Form = (props: any) => {
  return (
    <>
      <label>{props.label}:</label>
      <input
        className="w-1/2 mb-2"
        type="text"
        id={props.id}
        name={props.id}
        value={props.value}
      />
      <hr />
    </>
  );
};

export default Form;
