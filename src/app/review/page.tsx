// src/pages/review.tsx

"use client"

import React from 'react';
import { useEffect, useState } from 'react';
import ResultHeader from '../components/ResultHeader';
import Table from '../components/Table';
import IncludeAndCurateButton from '../components/IncludeAndCurateButton';

export default function Review() {
  // selected row and set selected rows from result page
  const [selectedRowsReview, setSelectedRowsReview] = useState([]);
  const [selectedRowsCurate, setSelectedRowsCurate] = useState([]);
  useEffect(() => {
    const storedRows = localStorage.getItem('selectedForReview');
    if (storedRows) {
      setSelectedRowsReview(JSON.parse(storedRows));
    };
  }, []);
  return (
    <div className='flex flex-col items-center justify-center min-h-screen'>
      {/*Rendering Select Signal Header componet */}
      <ResultHeader />
      <Table data={selectedRowsReview} setSelectedRows={setSelectedRowsCurate}/>
      <div className='flex space-x-5'>
      <IncludeAndCurateButton selectedRows={selectedRowsCurate}/>
      </div>
    </div>
  );
}
