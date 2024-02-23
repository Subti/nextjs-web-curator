// src/pages/result.tsx

import React from 'react';
import { useState } from 'react';
import SelectSignalHeader from '../components/SelectSignalHeader';

export default function ResultPage() {
  return (
    <div className="font-bold underline">
      {/*Rendering Select Signal Header componet */}
      <SelectSignalHeader />
    </div>
  );
};
