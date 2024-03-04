import React, { useState } from 'react';
import 'tailwindcss/tailwind.css';

// const CuratePage = () => {
//   return (
//     <div className="bg-blue-500 p-4 m-4 rounded-lg">
//       <h1 className="text-2xl font-bold text-white">Curate Page</h1>
//       <p className="mt-2 text-white">This is a simple webpage to demonstrate a light blue banner with white text using Tailwind CSS.</p>
//     </div>
//   );
// };

// export default CuratePage;

const CuratePage = () => {
  const [formData, setFormData] = useState({
    example_length: '512',
    class_1: 'protocol',
    class_2: 'use_case',
    dataset_name: 'collision.dat'
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle form submission logic here
  };

  return (
    <div className="container mx-auto px-10 py-8">
      <h1 className="text-4xl text-center font-bold mb-8">Dataset Curation</h1>
      <form onSubmit={handleSubmit} className="flex flex-col items-center justify-center">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl mb-4 font-bold">Recording summary</h2>
            {/* Display recording summary data */}
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
        <input type="submit" value="Prepare draft dataset" className="bg-blue-500 text-white px-6 py-3 rounded-full mt-8 cursor-pointer hover:bg-blue-600 transition duration-300" />
      </form>
    </div>
  );
};

export default CuratePage;
