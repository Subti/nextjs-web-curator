/* eslint-disable react/no-unescaped-entities */
import React, { useState } from 'react';
import Button from "@/app/components/Button";
import 'tailwindcss/tailwind.css';

const DatasetPage = () => {
  const [terminalOutput, setTerminalOutput] = useState('');

  // Draft dataset, pre-filtered
  /* This data should have been passed from /curate route to here, for further filtering later */
  const draftDataset = {
    pairs: [
      { key: "('Wifi-BGN', 'ambient')", num_examples: 7 }
    ],
    labels: [
      { index: "Wifi-BGN", ambient: 7, total: 7 },
      { index: "Total", ambient: 7, total: 7 }
    ],
    vectorLengths: [
      { label: "Wifi-BGN", length: 512 }
    ],
    statistics: {
      num_unique_classes: 1,
      total_examples: 7,
      first_labels: 1,
      second_labels: 1,
      typical_examples_per_class: 7,
      typical_vector_length: 512,
      largest_class: "('Wifi-BGN', 'ambient')",
      smallest_class: "('Wifi-BGN', 'ambient')"
    }
  };

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
      <h1 className="text-4xl text-center font-bold mb-8 text-white">Results of Dataset Curation:</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 text-white">

        <span className="flex-1">
          <h2 className="text-2xl mb-4 font-bold">Number of examples per unique pair</h2>
          <table className="table-auto text-center">
            <tbody>
              <tr>
                <th className="border px-4 py-2 font-bold">Key</th>
                <th className="border px-4 py-2 font-bold">num_examples</th>
              </tr>
              {draftDataset.pairs.map(pair => (
                <tr key={pair.key}>
                  <td className="border px-4 py-2">{pair.key}</td>
                  <td className="border px-4 py-2">{pair.num_examples}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </span>

        <span className="flex-1">
          <h2 className="text-2xl mb-4 font-bold">Number of examples per label</h2>
          <table className="table-auto">
            <tbody>
              <tr>
                <th className="border px-4 py-2 font-bold">Index</th>
                <th className="border px-4 py-2 font-bold">ambient</th>
                <th className="border px-4 py-2 font-bold">Total</th>
              </tr>
              {draftDataset.labels.map(label => (
                <tr key={label.index}>
                  <td className="border px-4 py-2">{label.index}</td>
                  <td className="border px-4 py-2">{label.ambient}</td>
                  <td className="border px-4 py-2">{label.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </span>

        <span className="flex-1">
          <h2 className="text-2xl mb-4 font-bold">Vector lengths per label</h2>
          <table className="table-auto">
            <tbody>
              <tr>
                <th className="border px-4 py-2 font-bold">ambient</th>
                <th className="border px-4 py-2 font-bold">length</th>
              </tr>
              {draftDataset.vectorLengths.map(vector => (
                <tr key={vector.label}>
                  <td className="border px-4 py-2">{vector.label}</td>
                  <td className="border px-4 py-2">{vector.length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </span>

      </div>

      <div className="flex mt-10 mb-20">
        <div className="flex-1 mr-4 text-white">
          <h2 className="text-2xl mb-4 font-bold">Dataset Statistics</h2>
          <table className="table-auto">
            <tbody>
              <tr>
                <th className="border px-4 py-2 font-bold">Index</th>
                <th className="border px-4 py-2 font-bold">Value</th>
              </tr>
              <tr>
                <td className="border px-4 py-2">Number of unique classes</td>
                <td className="border px-4 py-2">{draftDataset.statistics.num_unique_classes}</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Total number of examples in the dataset</td>
                <td className="border px-4 py-2">{draftDataset.statistics.total_examples}</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">First labels</td>
                <td className="border px-4 py-2">{draftDataset.statistics.first_labels}</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Second labels</td>
                <td className="border px-4 py-2">{draftDataset.statistics.second_labels}</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Typical number of examples per unique class</td>
                <td className="border px-4 py-2">{draftDataset.statistics.typical_examples_per_class}</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Typical example vector length</td>
                <td className="border px-4 py-2">{draftDataset.statistics.typical_vector_length}</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Class with largest number of examples</td>
                <td className="border px-4 py-2">{draftDataset.statistics.largest_class}</td>
              </tr>
              <tr>
                <td className="border px-4 py-2">Class with smallest number of examples</td>
                <td className="border px-4 py-2">{draftDataset.statistics.smallest_class}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="flex-1 mr-4">
          <h2 className="text-2xl mb-4 font-bold text-white">Dataset configuration:</h2>
          <form onSubmit={handleSubmit} className="flex flex-col items-center justify-center">
            <label htmlFor="homogenize" className="font-bold text-white">Subsample examples to a fixed maximum:</label>
            <input
              type="text"
              id="homogenize"
              name="homogenize"
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label htmlFor="augment" className="font-bold text-white">Fill gaps with augmentations:</label>
            <input
              type="text"
              id="augment"
              name="augment"
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label className="font-bold text-white">Drop Classes:</label>
            <div>
              <label htmlFor="drop_wifi_ambient" className="text-white cursor-pointer hover:text-blue-100 transition duration-300">
                <input type="checkbox" id="drop_wifi_ambient" name="drop_classes" value="wifi_ambient" className="mr-2" />
                Wifi-BGN, ambient
              </label>
            </div>
            <div className="flex justify-center w-full my-10 gap-5">
              <Button
                text="Prepare Final"
                type="button"
                textSize="xl"
                onClick={handlePrepareFinal}
              />
              <Button
                text="Download Draft"
                type="button"
                textSize="xl"
                onClick={handleDownloadDraft}
              />
            </div>
          </form>
        </div>

      </div>

      <div className="terminal-output bg-gray-900 text-white overflow-y-auto mt-8 p-4 rounded-md">
        <pre>{terminalOutput}</pre>
      </div>
      <div className="flex justify-center mt-8">
        <form onSubmit={handleSubmit}>
          <Button
            text="Clear all and reset"
            type="button"
            textSize="xl"
            onClick={handleClearAllAndReset}
          />
        </form>
      </div>

    </div>
  );
};

export default DatasetPage;