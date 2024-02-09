// import React from "react";

// const Column = (props: any) => {
//   return (
//     <div className="flex flex-col flex-grow bg-black w-1/2 h-20">
//       <h2 className="text-center">{props.title}</h2>
//     </div>
//   );
// };

// export default Column;

// Column.tsx
import React from "react";
import Form from "./Form";

interface FormData {
  label: string;
  id: string;
  name: string;
  value: string;
}

interface ColumnProps {
  title: string;
  forms: FormData[];
}

const Column: React.FC<ColumnProps> = ({ title, forms }) => {
  return (
    <div className="flex flex-col flex-grow bg-black w-1/2 px-3">
      <h2 className="text-center">{title}</h2>
      {forms.map((formData, index) => (
        <Form key={index} {...formData} />
      ))}
    </div>
  );
};

export default Column;
