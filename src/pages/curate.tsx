import React, { useState } from 'react';
import 'tailwindcss/tailwind.css';

const CuratePage = () => {
  const [formData, setFormData] = useState({
    example_length: '512',
    class_1: 'protocol',
    class_2: 'use_case',
    dataset_name: 'collision.dat'
  });

  // Sample recording summary data
  const recordingSummaryData = {
    protocol: "Wifi-BGN",
    use_case: "ambient",
    testbed: "Portable-Blade",
    transmitters: "Ambient",
    project_name: "Collision2023",
    sdr: "synthetic_sdr",
    center_freq: "2440000000.0",
    rec_length: "10000000",
    decimation: "1",
    hw_sample_rate: "20000000",
    effective_sample_rate: "20000000",
    signal_type: "Recorded Baseband-IQ",
    date_recorded: "03-22",
    time_recorded: "12:00 PM",
    filename: "recording001.npy"
  };


  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle form submission logic here
  };

  const handleClearAllAndReset = () => {
    // Display alert when "Clear all and reset" is clicked for testing only
    alert("Clear all and reset clicked!");
  };

  const handlePrepareDraftDataset = () => {
    // Display alert when "Prepare Draft Dataset" is clicked for testing only
    alert("Prepare Draft Dataset clicked!");

  };

  return (
    <div className="container mx-auto px-10 py-8">
      <div className="bg-blue-200 text-center py-2 rounded-md mb-8">
        <h1 className="text-4xl text-center font-bold mb-8">Dataset Curation</h1>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col items-center justify-center">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl mb-4 font-bold">Recording summary</h2>
            {/* Display recording summary data */}
            <table className="table-auto">
              <tbody>
                {Object.entries(recordingSummaryData).map(([key, value]) => (
                  <tr key={key}>
                    <td className="border px-4 py-2 font-bold">{key}</td>
                    <td className="border px-4 py-2">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {/* End of recording summary data */}
          </div>
          <div>
            <h2 className="text-2xl mb-4 font-bold">Dataset Configuration:</h2>
            <label htmlFor="example_length">Example Length:</label>
            <input
              type="text"
              id="example_length"
              name="example_length"
              value={formData.example_length}
              onChange={(e) => setFormData({ ...formData, example_length: e.target.value })}
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label htmlFor="class_1">Primary Label:</label>
            <input
              type="text"
              id="class_1"
              name="class_1"
              value={formData.class_1}
              onChange={(e) => setFormData({ ...formData, class_1: e.target.value })}
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label htmlFor="class_2">Second Label:</label>
            <input
              type="text"
              id="class_2"
              name="class_2"
              value={formData.class_2}
              onChange={(e) => setFormData({ ...formData, class_2: e.target.value })}
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
            <label htmlFor="dataset_name">Filename:</label>
            <input
              type="text"
              id="dataset_name"
              name="dataset_name"
              value={formData.dataset_name}
              onChange={(e) => setFormData({ ...formData, dataset_name: e.target.value })}
              className="border border-gray-300 rounded-md p-2 w-full mb-4"
            />
          </div>
        </div>
        <input onClick={handlePrepareDraftDataset} type="submit" value="Prepare draft dataset" className="bg-blue-500 text-white px-6 py-3 rounded-full mt-8 mb-10 cursor-pointer hover:bg-blue-600 transition duration-300" />
        <input onClick={handleClearAllAndReset} type="submit" value="Clear all and reset" className="bg-blue-500 text-white px-6 py-3 rounded-full mt-8 cursor-pointer hover:bg-blue-600 transition duration-300" />
      </form>
    </div>
  );
};

export default CuratePage;
