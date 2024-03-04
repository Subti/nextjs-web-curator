"use client" 

import React, { useState } from 'react';
import DataTable from 'react-data-table-component';

interface DataRow {
  id: number;
  plot: string;
  fileName: string;
  projectName: string;
  centerFrequency: number;
  sampleRate: number;
  protocol: string;
  usage: string;
}

interface TableProps {
  setSelectedRows: React.Dispatch<React.SetStateAction<DataRow[]>>;
  data: DataRow[];
}

const Table: React.FC<TableProps> = ({ setSelectedRows, data })  => {
  // const [selectedRows, setSelectedRows] = useState<DataRow[]>([]); // State to keep track of selected rows
  const handleRowSelected = (state) => {
    setSelectedRows(state.selectedRows);
  };
  const hardcodedData: DataRow[] = [
    {
      id: 1,
      plot: 'http://localhost:8000/static/Wifi-BGN/3_iq2440MHz224846.svg',
      fileName: '1_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 2,
      plot: 'http://localhost:8000/static/Wifi-BGN/0_iq2440MHz224846.svg',
      fileName: '2_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 3,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: '3_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 4,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: '4_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 5,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: '5_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 6,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: '6_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 7,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: '7_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 8,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: '8_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 9,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: '9_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 10,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: '10_iq2440MHz224846',
      projectName: 'Collision2023',
      centerFrequency: 2440000000.0	,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 11,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: 'this file 2',
      projectName: 'my project',
      centerFrequency: 21010101,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
    {
      id: 12,
      plot: 'http://localhost:8000/static/Wifi-BGN/1_iq2440MHz224846.svg',
      fileName: 'this file 3',
      projectName: 'my project',
      centerFrequency: 3330033,
      sampleRate: 20.0,
      protocol: 'Wifi-BGN	',
      usage: 'ambient'
    },
  ];
  const tableData = data?.length > 0 ? data : hardcodedData;
  
  const columns = [
    {
      name: "IQ Plot and Spectrogram",
      selector: (row: DataRow) => row.plot,
      cell: (row: DataRow) => <img src={row.plot} alt="Plot" style={{ width: 'auto', height: 'auto' }} />, // Display image
      sortable: true,
    },
    {
      name: "File",
      selector: (row: DataRow) => row.fileName,
      sortable: true,
    },
    {
      name: "Project Name",
      selector: (row: DataRow) => row.projectName,
      sortable: true,
    },
    {
      name: "Center Frequency (MHz)",
      selector: (row: DataRow) => row.centerFrequency,
      sortable: true,
      format: (row: DataRow) => `${row.centerFrequency.toLocaleString()} MHz`, // Formatting numbers
    },
    {
      name: "Protocol",
      selector: (row: DataRow) => row.protocol,
      sortable: true,
    },
    {
      name: "Usage",
      selector: (row: DataRow) => row.usage,
      sortable: true,
    }
  ];


  return (
    <div>
      <h2 className='bold'>Title based on protocol</h2>
      <DataTable
        columns={columns}
        data={tableData}
        pagination // Add pagination
        selectableRows // Enable row selection
        onSelectedRowsChange={handleRowSelected} // Handle row selection changes
      />
      {/* <button 
        className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        onClick={handleSaveSelected}>Save and Capture More
      </button> */}
    </div>
  );
};

export default Table;