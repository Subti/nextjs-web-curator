// src/pages/result.tsx

"use client"

import React from 'react';
import { useState } from 'react';
import ResultHeader from '../components/ResultHeader';
import Table from '../components/Table';
import SaveAndCaptureButton from '../components/SaveAndCaptureButton';
import IncludeAndReviewButton from '../components/IncludeAndReviewButton';

export default function ResultPage() {

  const [selectedRows, setSelectedRows] = useState([]);

  return (
    <div className='flex flex-col items-center justify-center min-h-screen'>
      {/*Rendering Select Signal Header componet */}
      <ResultHeader />
      <Table setSelectedRows={setSelectedRows}/>
      <div className='flex space-x-5'>
      <SaveAndCaptureButton selectedRows={selectedRows} />
      <IncludeAndReviewButton selectedRows={selectedRows} />
      </div>
    </div>
  );
};
