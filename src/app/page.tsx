// import Button from "./components/Button";
// import Column from "./components/Column";
// import Header from "./components/Header";
// import Row from "./components/Row";
// import Form from "./components/Form";

// export default function Home() {
//   return (
//     <>
//       <main className="flex flex-col items-center justify-center min-h-screen">
//         <Header />
//         <div className="flex flex-grow bg-white w-1/2">
//           <Column title="Capture Settings">
//             <Form
//               label="IP Address"
//               id="ip_address"
//               name="ip_address"
//               value="192.168.40.2"
//             />
//           </Column>
//           <Column title="Metadata" />
//         </div>
//         <Button />
//       </main>
//     </>
//   );
// }

// Home.tsx
import React from "react";
import Button from "./components/Button";
import Column from "./components/Column";
import Header from "./components/Header";

export default function Home() {
  const captureSettingsForms = [
    {
      label: "IP Address",
      id: "ip_address",
      name: "ip_address",
      value: "192.168.40.2"
    }
    // Add more form data objects as needed
  ];

  const metadataForms = [
    {
      label: "Protocol",
      id: "protocol",
      name: "protocol",
      value: "Wifi-BGN"
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <Header />
      <div className="flex flex-grow bg-white w-1/2">
        <Column title="Capture Settings" forms={captureSettingsForms} />
        <Column title="Metadata" forms={metadataForms} />
      </div>
      <div className="flex justify-end">
        <Button />
      </div>
    </div>
  );
}
