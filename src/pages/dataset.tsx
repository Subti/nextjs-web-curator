/* eslint-disable react/no-unescaped-entities */
import React, { useState } from 'react';
import 'tailwindcss/tailwind.css';

const DatasetPage = () => {
  const [terminalOutput, setTerminalOutput] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle form submission logic here
  };

  const handleClearAllAndReset = () => {
    // Display alert when "Clear all and reset" is clicked for testing only
    alert("Clear all and reset clicked!");
  };

  const handlePrepareFinal = () => {
    // Display alert when "Prepare Final" is clicked for testing only
    alert("Prepare Final clicked!");

  };

  const handleDownloadDraft = () => {
    // Display alert when "Download Draft" is clicked for testing only
    alert("Download Draft clicked!");

  };

  return (
    <div className="container mx-auto px-10 py-8">
      <h1 className="text-4xl text-center font-bold mb-8">Results of Dataset Curation:</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10">

        <span className="flex-1">
          <h2 className="text-2xl mb-4 font-bold">Number of examples per unique pair</h2>
          {/* Display dataset review results */}
          <table className="table-auto text-center">
            <tbody>
              {/* Sample data */}
              <tr>
                <th className="border px-4 py-2 font-bold">Key</th>
                <th className="border px-4 py-2 font-bold">num_examples</th>
              </tr>
              <tr>
                <td className="border px-4 py-2">('Wifi-BGN', 'ambient')</td>
                <td className="border px-4 py-2">7</td>
              </tr>
              {/* Add more rows as needed */}
            </tbody>
          </table>
        </span>

        <span className="flex-1">
          <h2 className="text-2xl mb-4 font-bold">Number of examples per label</h2>
          {/* Display dataset review results */}
          <table className="table-auto">
            <tbody>
              {/* Sample data */}
              <tr>
                <th className="border px-4 py-2 font-bold">Index</th>
                <th className="border px-4 py-2 font-bold">ambient</th>
                <th className="border px-4 py-2 font-bold">Total</th>
              </tr>
              <tr>
                <td className="border px-4 py-2">Wifi-BGN</td>
                <td className="border px-4 py-2">7</td>
                <td className="border px-4 py-2">7</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Total</td>
                <td className="border px-4 py-2">7</td>
                <td className="border px-4 py-2">7</td>
              </tr>
              {/* Add more rows as needed */}
            </tbody>
          </table>
        </span>

        <span className="flex-1">
          <h2 className="text-2xl mb-4 font-bold">Vector lengths per label</h2>
          {/* Display dataset review results */}
          <table className="table-auto">
            <tbody>
              {/* Sample data */}
              <tr>
                <th className="border px-4 py-2 font-bold">ambient</th>
                <th className="border px-4 py-2 font-bold">length</th>
              </tr>
              <tr>
                <td className="border px-4 py-2">Wifi-BGN</td>
                <td className="border px-4 py-2">512</td>
              </tr>
              {/* Add more rows as needed */}
            </tbody>
          </table>
        </span>


      </div>

      <div className="flex mt-10 mb-20">


        <div className="flex-1 mr-4">
          <h2 className="text-2xl mb-4 font-bold">Dataset Statistics</h2>
          <table className="table-auto">
            <tbody>
              {/* Sample data */}
              <tr>
                <th className="border px-4 py-2 font-bold">Index</th>
                <th className="border px-4 py-2 font-bold">Value</th>
              </tr>
              <tr>
                <td className="border px-4 py-2">Number of unique classes</td>
                <td className="border px-4 py-2">1</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Total number of examples in the dataset</td>
                <td className="border px-4 py-2">7</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">First labels</td>
                <td className="border px-4 py-2">1</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Second labels</td>
                <td className="border px-4 py-2">1</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Typical number of examples per unique class</td>
                <td className="border px-4 py-2">7</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Typical example vector length</td>
                <td className="border px-4 py-2">512</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Class with largest number of examples</td>
                <td className="border px-4 py-2">('Wifi-BGN', 'ambient')</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Class with smallest number of examples</td>
                <td className="border px-4 py-2">('Wifi-BGN', 'ambient')</td>
              </tr>
              {/* Add more rows as needed */}
            </tbody>
          </table>
        </div>

        <div className="flex-1 mr-4">
          <h2 className="text-2xl mb-4 font-bold">Dataset configuration:</h2>
          <form onSubmit={handleSubmit} className="flex flex-col items-center justify-center">
            <label htmlFor="homogenize" className="font-bold">Subsample examples to a fixed maximum:</label>
            <input
              type="text"
              id="homogenize"
              name="homogenize"
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label htmlFor="augment" className="font-bold">Fill gaps with augmentations:</label>
            <input
              type="text"
              id="augment"
              name="augment"
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label className="font-bold">Drop Classes:</label>
            {/* Checkboxes for dropping classes */}
            <div>
              <label htmlFor="drop_wifi_ambient" className="cursor-pointer hover:text-blue-600 transition duration-300">
                <input type="checkbox" id="drop_wifi_ambient" name="drop_classes" value="wifi_ambient" className="mr-2" />
                Wifi-BGN, ambient
              </label>
            </div>
            <input onClick={handlePrepareFinal} type="submit" value="Prepare Final" className="bg-blue-500 text-white px-6 py-3 rounded-full mt-8 cursor-pointer hover:bg-blue-600 hover:pointer transition duration-300" />
            <button onClick={handleDownloadDraft} className="bg-blue-500 text-white px-6 py-3 rounded-full mt-8 cursor-pointer hover:bg-blue-600 hover:pointer transition duration-300">Download Draft</button>
          </form>
        </div>

      </div>

      <div className="terminal-output bg-gray-900 text-white overflow-y-auto mt-8 p-4 rounded-md">
        <pre>{terminalOutput}</pre>
      </div>
      <div className="flex justify-center mt-8">
        <form onSubmit={handleSubmit}>
          <button onClick={handleClearAllAndReset} type="submit" className="bg-blue-500 text-white px-6 py-3 rounded-full cursor-pointer hover:bg-blue-600 transition duration-300">
            Clear all and reset
          </button>
        </form>
      </div>

    </div>
  );
};

export default DatasetPage;