import React, { useState } from 'react';
import 'tailwindcss/tailwind.css';

// const DatasetPage = () => {
//   return (
//     <div className="bg-blue-500 p-4 m-4 rounded-lg">
//       <h1 className="text-2xl font-bold text-white">Dataset Page</h1>
//       <p className="mt-2 text-white">This is a simple webpage to demonstrate a light blue banner with white text using Tailwind CSS.</p>
//     </div>
//   );
// };

// export default DatasetPage;

const DatasetPage = () => {
  const [terminalOutput, setTerminalOutput] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle form submission logic here
  };

  return (
    <div className="container mx-auto px-10 py-8">
      <h1 className="text-4xl text-center font-bold mb-8">Results of Dataset Curation:</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl mb-4 font-bold">Number of examples per unique pair</h2>
          {/* Display dataset review results */}
        </div>
        <div>
          <h2 className="text-2xl mb-4 font-bold">Dataset configuration:</h2>
          <form onSubmit={handleSubmit} className="flex flex-col items-center justify-center">
            <label htmlFor="homogenize">Subsample examples to a fixed maximum:</label>
            <input
              type="text"
              id="homogenize"
              name="homogenize"
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label htmlFor="augment">Fill gaps with augmentations:</label>
            <input
              type="text"
              id="augment"
              name="augment"
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label>Drop Classes:</label>
            {/* Checkboxes for dropping classes */}
            <input type="submit" value="Prepare Final" className="bg-blue-500 text-white px-6 py-3 rounded-full mt-8 cursor-pointer hover:bg-blue-600 transition duration-300" />
          </form>
        </div>
      </div>
      <button className="bg-blue-500 text-white px-6 py-3 rounded-full mt-8 cursor-pointer hover:bg-blue-600 transition duration-300">Download Draft</button>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
        <div>
          <h2 className="text-2xl mb-4 font-bold">Dataset Statistics</h2>
          {/* Display dataset statistics */}
        </div>
        <div>
          <h2 className="text-2xl mb-4 font-bold">Dataset Image</h2>
          {/* Display dataset image */}
        </div>
      </div>
      <div className="terminal-output bg-gray-900 text-white overflow-y-auto mt-8 p-4 rounded-md">
        <pre>{terminalOutput}</pre>
      </div>
      <form className="mt-8" onSubmit={handleSubmit}>
        <button type="submit" className="bg-blue-500 text-white px-6 py-3 rounded-full cursor-pointer hover:bg-blue-600 transition duration-300">Clear all and reset</button>
      </form>
    </div>
  );
};

export default DatasetPage;
